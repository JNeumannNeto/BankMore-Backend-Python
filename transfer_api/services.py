import logging
import requests
from decimal import Decimal
from django.db import transaction
from django.db.models import Q
from django.conf import settings
from .models import Transfer
from account_api.models import Account
from shared.utils import MovementTypes, TransferStatus
from shared.services import IdempotencyService, CacheService, kafka_service
from shared.exceptions import BankMoreException, ErrorTypes

logger = logging.getLogger('bankmore')


class AccountApiService:
    @staticmethod
    def create_movement(account_number: str, amount: Decimal, movement_type: str, request_id: str):
        try:
            account_api_url = getattr(settings, 'ACCOUNT_API_BASE_URL', 'http://localhost:8001')
            
            response = requests.post(
                f"{account_api_url}/api/account/movement/",
                json={
                    'request_id': request_id,
                    'account_number': account_number,
                    'amount': str(amount),
                    'type': movement_type
                },
                timeout=30
            )
            
            if response.status_code not in [200, 204]:
                logger.error(f"Account API error: {response.status_code} - {response.text}")
                raise BankMoreException(
                    "Erro ao processar movimentação na conta",
                    ErrorTypes.INTERNAL_ERROR
                )
                
            return True
            
        except requests.RequestException as e:
            logger.error(f"Account API request failed: {e}")
            raise BankMoreException(
                "Erro de comunicação com a API de contas",
                ErrorTypes.INTERNAL_ERROR
            )


class TransferService:
    @staticmethod
    def create_transfer(request_id: str, origin_account_id: str, destination_account_number: str, amount: Decimal) -> dict:
        cached_response = IdempotencyService.check_idempotency(
            request_id,
            {
                'origin_account_id': origin_account_id,
                'destination_account_number': destination_account_number,
                'amount': str(amount)
            }
        )
        
        if cached_response:
            return cached_response
        
        try:
            origin_account = Account.objects.get(id=origin_account_id)
            destination_account = Account.objects.get(number=destination_account_number)
            
            if not origin_account.active:
                raise BankMoreException(
                    "Conta de origem inativa",
                    ErrorTypes.INACTIVE_ACCOUNT
                )
            
            if not destination_account.active:
                raise BankMoreException(
                    "Conta de destino inativa",
                    ErrorTypes.INACTIVE_ACCOUNT
                )
            
            if origin_account.number == destination_account.number:
                raise BankMoreException(
                    "Não é possível transferir para a mesma conta",
                    ErrorTypes.INVALID_TRANSFER
                )
            
            current_balance = origin_account.get_balance()
            if current_balance < amount:
                raise BankMoreException(
                    "Saldo insuficiente",
                    ErrorTypes.INSUFFICIENT_BALANCE
                )
            
            with transaction.atomic():
                transfer = Transfer.objects.create(
                    origin_account=origin_account,
                    destination_account=destination_account,
                    amount=amount,
                    description=f"Transferência para conta {destination_account.number}",
                    idempotency_key=request_id
                )
                
                try:
                    debit_request_id = f"{request_id}-debit"
                    AccountApiService.create_movement(
                        origin_account.number,
                        amount,
                        MovementTypes.DEBIT,
                        debit_request_id
                    )
                    
                    credit_request_id = f"{request_id}-credit"
                    AccountApiService.create_movement(
                        destination_account.number,
                        amount,
                        MovementTypes.CREDIT,
                        credit_request_id
                    )
                    
                    transfer.mark_completed()
                    
                    cache_key_origin = CacheService.get_account_balance_key(origin_account.number)
                    cache_key_dest = CacheService.get_account_balance_key(destination_account.number)
                    CacheService.delete(cache_key_origin)
                    CacheService.delete(cache_key_dest)
                    
                    transfer_data = {
                        'id': str(transfer.id),
                        'origin_account_number': origin_account.number,
                        'destination_account_number': destination_account.number,
                        'amount': str(amount),
                        'request_id': request_id
                    }
                    
                    kafka_service.send_transfer_completed(transfer_data)
                    
                    logger.info(f"Transfer completed: {transfer.id} from {origin_account.number} to {destination_account.number}")
                    
                    response = {
                        'transfer_id': str(transfer.id),
                        'message': 'Transferência realizada com sucesso',
                        'origin_account_number': origin_account.number,
                        'destination_account_number': destination_account.number,
                        'amount': amount
                    }
                    
                    IdempotencyService.save_response(request_id, response)
                    return response
                    
                except Exception as e:
                    transfer.mark_failed()
                    logger.error(f"Transfer failed: {e}")
                    raise
                    
        except Account.DoesNotExist:
            raise BankMoreException(
                "Conta não encontrada",
                ErrorTypes.ACCOUNT_NOT_FOUND
            )
    
    @staticmethod
    def get_transfers_by_account(account_id: str) -> list:
        try:
            account = Account.objects.get(id=account_id)
            
            transfers = Transfer.objects.filter(
                Q(origin_account=account) | Q(destination_account=account)
            ).select_related('origin_account', 'destination_account').order_by('-created_at')
            
            return list(transfers)
            
        except Account.DoesNotExist:
            raise BankMoreException(
                "Conta não encontrada",
                ErrorTypes.ACCOUNT_NOT_FOUND
            )
    
    @staticmethod
    def get_transfer_by_id(transfer_id: str, account_id: str) -> Transfer:
        try:
            account = Account.objects.get(id=account_id)
            
            transfer = Transfer.objects.select_related(
                'origin_account', 'destination_account'
            ).get(
                id=transfer_id
            )
            
            if transfer.origin_account != account and transfer.destination_account != account:
                raise Transfer.DoesNotExist()
            
            return transfer
            
        except Account.DoesNotExist:
            raise BankMoreException(
                "Conta não encontrada",
                ErrorTypes.ACCOUNT_NOT_FOUND
            )
        except Transfer.DoesNotExist:
            raise BankMoreException(
                "Transferência não encontrada",
                ErrorTypes.INVALID_TRANSFER
            )
