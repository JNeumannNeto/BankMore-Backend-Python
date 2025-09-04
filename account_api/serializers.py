from rest_framework import serializers
from decimal import Decimal
from .models import Account, Movement
from shared.utils import CPFValidator, PasswordHasher, MovementTypes, MoneyUtils
from shared.exceptions import BankMoreException, ErrorTypes


class CreateAccountSerializer(serializers.Serializer):
    cpf = serializers.CharField(max_length=11)
    name = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=100, write_only=True)
    
    def validate_cpf(self, value):
        cpf_clean = CPFValidator.clean(value)
        if not CPFValidator.validate(cpf_clean):
            raise BankMoreException(
                "CPF inválido",
                ErrorTypes.INVALID_DOCUMENT
            )
        
        if Account.objects.filter(cpf=cpf_clean).exists():
            raise BankMoreException(
                "CPF já cadastrado",
                ErrorTypes.INVALID_DOCUMENT
            )
        
        return cpf_clean
    
    def validate_name(self, value):
        if not value or len(value.strip()) < 2:
            raise BankMoreException(
                "Nome deve ter pelo menos 2 caracteres",
                ErrorTypes.INVALID_ARGUMENT
            )
        return value.strip()
    
    def validate_password(self, value):
        if not value or len(value) < 6:
            raise BankMoreException(
                "Senha deve ter pelo menos 6 caracteres",
                ErrorTypes.INVALID_ARGUMENT
            )
        return value


class LoginSerializer(serializers.Serializer):
    cpf = serializers.CharField(max_length=11)
    password = serializers.CharField(max_length=100, write_only=True)
    
    def validate_cpf(self, value):
        return CPFValidator.clean(value)


class CreateMovementSerializer(serializers.Serializer):
    request_id = serializers.CharField(max_length=255)
    account_number = serializers.CharField(max_length=10)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    type = serializers.CharField(max_length=1)
    
    def validate_amount(self, value):
        if not MoneyUtils.validate_amount(value):
            raise BankMoreException(
                "Valor deve ser positivo",
                ErrorTypes.INVALID_VALUE
            )
        return value
    
    def validate_type(self, value):
        if not MovementTypes.is_valid(value):
            raise BankMoreException(
                "Tipo de movimento inválido",
                ErrorTypes.INVALID_TYPE
            )
        return value


class DeactivateAccountSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=100, write_only=True)


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'number', 'name', 'cpf', 'active', 'created_at']
        read_only_fields = ['id', 'number', 'created_at']


class MovementSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Movement
        fields = ['id', 'amount', 'type', 'type_display', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class BalanceSerializer(serializers.Serializer):
    account_number = serializers.CharField()
    balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    account_name = serializers.CharField()


class CreateAccountResponseSerializer(serializers.Serializer):
    account_number = serializers.CharField()
    message = serializers.CharField()


class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    account_number = serializers.CharField()
    name = serializers.CharField()
