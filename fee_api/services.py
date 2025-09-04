import logging
import requests
from decimal import Decimal
from django.db import transaction
from django.conf import settings
from .models import Fee
from account_api.models import Account
from shared.utils import MovementTypes
from shared.services import CacheService
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
                return False
                
            return True
            
        except requests.RequestException as e:
            logger.error(f"Account API request failed: {e}")
            return False


class FeeService:
    @staticmethod
    def process_transfer_fee(transfer_data: dict):
        try:
            origin_account_number = transfer_data.get('origin_account_number')
            destination_account_number = transfer_data.get('destination_account_number')
            transfer_amount = Decimal(transfer_data.get('amount', '0'))
            request_id = transfer_data.get('request_id')
            
            fee_settings = settings.FEE_SETTINGS
            fee_amount = Decimal(str(fee_settings['TRANSFER_FEE_AMOUNT']))
            
            try:
                origin_account = Account.objects.get(number=origin_account_number)
                
                if not origin_account.active:
                    logger.warning(f"Cannot charge fee for inactive account: {origin_account_number}")
                    return
                
                with transaction.atomic():
                    fee = Fee.objects.create(
                        account=origin_account,
                        amount=fee_amount,
                        type='TRANSFER',
                        description=f'Taxa de transferência - Destino: {destination_account_number}',
                        request_id=f"{request_id}-fee"
                    )
                    
                    fee_request_id = f"{request_id}-fee-debit"
                    success = AccountApiService.create_movement(
                        origin_account_number,
                        fee_amount,
                        MovementTypes.DEBIT,
                        fee_request_id
                    )
                    
                    if success:
                        cache_key = CacheService.get_account_balance_key(origin_account_number)
                        CacheService.delete(cache_key)
                        
                        logger.info(f"Transfer fee processed: {fee.id} for account {origin_account_number}")
                    else:
                        logger.error(f"Failed to debit fee for account {origin_account_number}")
                        
            except Account.DoesNotExist:
                logger.error(f"Account not found for fee processing: {origin_account_number}")
                
        except Exception as e:
            logger.error(f"Error processing transfer fee: {e}")
    
    @staticmethod
    def get_fees_by_account_number(account_number: str) -> list:
        try:
            account = Account.objects.get(number=account_number)
            
            fees = Fee.objects.filter(account=account).order_by('-created_at')
            return list(fees)
            
        except Account.DoesNotExist:
            raise BankMoreException(
                "Conta não encontrada",
                ErrorTypes.ACCOUNT_NOT_FOUND
            )
    
    @staticmethod
    def get_fee_by_id(fee_id: str) -> Fee:
        try:
            fee = Fee.objects.select_related('account').get(id=fee_id)
            return fee
            
        except Fee.DoesNotExist:
            raise BankMoreException(
                "Tarifa não encontrada",
                ErrorTypes.INVALID_OPERATION
            )
    
    @staticmethod
    def get_fees_by_account_id(account_id: str) -> list:
        try:
            account = Account.objects.get(id=account_id)
            
            fees = Fee.objects.filter(account=account).order_by('-created_at')
            return list(fees)
            
        except Account.DoesNotExist:
            raise BankMoreException(
                "Conta não encontrada",
                ErrorTypes.ACCOUNT_NOT_FOUND
            )
