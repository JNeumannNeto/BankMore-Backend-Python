from rest_framework import serializers
from decimal import Decimal
from .models import Transfer
from account_api.models import Account
from shared.utils import MoneyUtils
from shared.exceptions import BankMoreException, ErrorTypes


class CreateTransferSerializer(serializers.Serializer):
    request_id = serializers.CharField(max_length=255)
    destination_account_number = serializers.CharField(max_length=10)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    def validate_amount(self, value):
        if not MoneyUtils.validate_amount(value):
            raise BankMoreException(
                "Valor deve ser positivo",
                ErrorTypes.INVALID_VALUE
            )
        return value
    
    def validate_destination_account_number(self, value):
        if not Account.objects.filter(number=value, active=True).exists():
            raise BankMoreException(
                "Conta de destino não encontrada ou inativa",
                ErrorTypes.ACCOUNT_NOT_FOUND
            )
        return value


class TransferSerializer(serializers.ModelSerializer):
    origin_account_number = serializers.CharField(source='origin_account.number', read_only=True)
    destination_account_number = serializers.CharField(source='destination_account.number', read_only=True)
    origin_account_name = serializers.CharField(source='origin_account.name', read_only=True)
    destination_account_name = serializers.CharField(source='destination_account.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Transfer
        fields = [
            'id', 'amount', 'status', 'status_display', 'description',
            'origin_account_number', 'destination_account_number',
            'origin_account_name', 'destination_account_name',
            'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'completed_at']


class TransferResponseSerializer(serializers.Serializer):
    transfer_id = serializers.UUIDField()
    message = serializers.CharField()
    origin_account_number = serializers.CharField()
    destination_account_number = serializers.CharField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
