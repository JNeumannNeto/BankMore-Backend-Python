import logging
from decimal import Decimal
from django.db import transaction
from .models import Account, Movement
from shared.utils import PasswordHasher, MovementTypes
from shared.authentication import JWTService
from shared.services import IdempotencyService, CacheService
from shared.exceptions import BankMoreException, ErrorTypes

logger = logging.getLogger('bankmore')


class AccountService:
    @staticmethod
    def create_account(cpf: str, name: str, password: str) -> dict:
        salt = PasswordHasher.generate_salt()
        password_hash = PasswordHasher.hash_password(password, salt)
        
        with transaction.atomic():
            account = Account.objects.create(
                cpf=cpf,
                name=name,
                password_hash=password_hash,
                salt=salt
            )
            
            logger.info(f"Account created: {account.number} for CPF: {cpf}")
            
            return {
                'account_number': account.number,
                'message': 'Conta criada com sucesso'
            }
    
    @staticmethod
    def authenticate(cpf: str, password: str) -> dict:
        try:
            account = Account.objects.get(cpf=cpf)
            
            if not account.active:
                raise BankMoreException(
                    "Conta inativa",
                    ErrorTypes.INACTIVE_ACCOUNT
                )
            
            if not account.verify_password(password):
                raise BankMoreException(
                    "CPF ou senha inválidos",
                    ErrorTypes.USER_UNAUTHORIZED
                )
            
            account_data = {
                'id': account.id,
                'number': account.number,
                'cpf': account.cpf,
                'name': account.name
            }
            
            token = JWTService.generate_token(account_data)
            
            logger.info(f"User authenticated: {account.number}")
            
            return {
                'token': token,
                'account_number': account.number,
                'name': account.name
            }
            
        except Account.DoesNotExist:
            raise BankMoreException(
                "CPF ou senha inválidos",
                ErrorTypes.USER_UNAUTHORIZED
            )
    
    @staticmethod
    def deactivate_account(account_id: str, password: str):
        try:
            account = Account.objects.get(id=account_id)
            
            if not account.verify_password(password):
                raise BankMoreException(
                    "Senha inválida",
                    ErrorTypes.USER_UNAUTHORIZED
                )
            
            account.deactivate()
            
            cache_key = CacheService.get_account_balance_key(account.number)
            CacheService.delete(cache_key)
            
            logger.info(f"Account deactivated: {account.number}")
            
        except Account.DoesNotExist:
            raise BankMoreException(
                "Conta não encontrada",
                ErrorTypes.ACCOUNT_NOT_FOUND
            )
    
    @staticmethod
    def create_movement(request_id: str, account_number: str, amount: Decimal, movement_type: str, user_account_id: str = None):
        cached_response = IdempotencyService.check_idempotency(
            request_id,
            {
                'account_number': account_number,
                'amount': str(amount),
                'type': movement_type
            }
        )
        
        if cached_response:
            return cached_response
        
        try:
            account = Account.objects.get(number=account_number)
            
            if not account.active:
                raise BankMoreException(
                    "Conta inativa",
                    ErrorTypes.INACTIVE_ACCOUNT
                )
            
            if user_account_id and str(account.id) != user_account_id:
                raise BankMoreException(
                    "Operação não autorizada para esta conta",
                    ErrorTypes.INVALID_OPERATION
                )
            
            if movement_type == MovementTypes.DEBIT:
                current_balance = account.get_balance()
                if current_balance < amount:
                    raise BankMoreException(
                        "Saldo insuficiente",
                        ErrorTypes.INSUFFICIENT_BALANCE
                    )
            
            with transaction.atomic():
                movement = Movement.objects.create(
                    account=account,
                    amount=amount,
                    type=movement_type,
                    idempotency_key=request_id
                )
                
                cache_key = CacheService.get_account_balance_key(account.number)
                CacheService.delete(cache_key)
                
                logger.info(f"Movement created: {movement.type} {movement.amount} for account {account.number}")
                
                response = {'message': 'Movimentação realizada com sucesso'}
                IdempotencyService.save_response(request_id, response)
                
                return response
                
        except Account.DoesNotExist:
            raise BankMoreException(
                "Conta não encontrada",
                ErrorTypes.ACCOUNT_NOT_FOUND
            )
    
    @staticmethod
    def get_balance(account_id: str) -> dict:
        try:
            account = Account.objects.get(id=account_id)
            
            cache_key = CacheService.get_account_balance_key(account.number)
            cached_balance = CacheService.get(cache_key)
            
            if cached_balance is not None:
                return {
                    'account_number': account.number,
                    'balance': cached_balance,
                    'account_name': account.name
                }
            
            balance = account.get_balance()
            CacheService.set(cache_key, balance, timeout=300)
            
            return {
                'account_number': account.number,
                'balance': balance,
                'account_name': account.name
            }
            
        except Account.DoesNotExist:
            raise BankMoreException(
                "Conta não encontrada",
                ErrorTypes.ACCOUNT_NOT_FOUND
            )
    
    @staticmethod
    def get_balance_by_account_number(account_number: str) -> dict:
        try:
            account = Account.objects.get(number=account_number)
            
            if not account.active:
                raise BankMoreException(
                    "Conta inativa",
                    ErrorTypes.INACTIVE_ACCOUNT
                )
            
            cache_key = CacheService.get_account_balance_key(account.number)
            cached_balance = CacheService.get(cache_key)
            
            if cached_balance is not None:
                return {
                    'account_number': account.number,
                    'balance': cached_balance,
                    'account_name': account.name
                }
            
            balance = account.get_balance()
            CacheService.set(cache_key, balance, timeout=300)
            
            return {
                'account_number': account.number,
                'balance': balance,
                'account_name': account.name
            }
            
        except Account.DoesNotExist:
            raise BankMoreException(
                "Conta não encontrada",
                ErrorTypes.ACCOUNT_NOT_FOUND
            )
    
    @staticmethod
    def account_exists(account_number: str) -> bool:
        return Account.objects.filter(number=account_number, active=True).exists()
