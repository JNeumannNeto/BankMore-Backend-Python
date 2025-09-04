import hashlib
import secrets
import re
from decimal import Decimal


class CPFValidator:
    @staticmethod
    def validate(cpf: str) -> bool:
        if not cpf or not isinstance(cpf, str):
            return False
        
        cpf = re.sub(r'[^0-9]', '', cpf)
        
        if len(cpf) != 11:
            return False
        
        if cpf == cpf[0] * 11:
            return False
        
        def calculate_digit(cpf_digits, weights):
            total = sum(int(digit) * weight for digit, weight in zip(cpf_digits, weights))
            remainder = total % 11
            return 0 if remainder < 2 else 11 - remainder
        
        first_digit = calculate_digit(cpf[:9], range(10, 1, -1))
        if int(cpf[9]) != first_digit:
            return False
        
        second_digit = calculate_digit(cpf[:10], range(11, 1, -1))
        if int(cpf[10]) != second_digit:
            return False
        
        return True

    @staticmethod
    def format(cpf: str) -> str:
        cpf = re.sub(r'[^0-9]', '', cpf)
        if len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        return cpf

    @staticmethod
    def clean(cpf: str) -> str:
        return re.sub(r'[^0-9]', '', cpf) if cpf else ""


class PasswordHasher:
    @staticmethod
    def generate_salt() -> str:
        return secrets.token_hex(32)
    
    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, salt: str, hashed_password: str) -> bool:
        return PasswordHasher.hash_password(password, salt) == hashed_password


class AccountNumberGenerator:
    @staticmethod
    def generate() -> str:
        return str(secrets.randbelow(900000) + 100000)


class MoneyUtils:
    @staticmethod
    def validate_amount(amount) -> bool:
        try:
            decimal_amount = Decimal(str(amount))
            return decimal_amount > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def format_currency(amount) -> str:
        return f"R$ {amount:.2f}".replace('.', ',')
    
    @staticmethod
    def to_decimal(amount) -> Decimal:
        return Decimal(str(amount))


class MovementTypes:
    CREDIT = 'C'
    DEBIT = 'D'
    
    CHOICES = [
        (CREDIT, 'Crédito'),
        (DEBIT, 'Débito'),
    ]
    
    @staticmethod
    def is_valid(movement_type: str) -> bool:
        return movement_type in [MovementTypes.CREDIT, MovementTypes.DEBIT]


class TransferStatus:
    PENDING = 0
    COMPLETED = 1
    FAILED = 2
    
    CHOICES = [
        (PENDING, 'Pendente'),
        (COMPLETED, 'Concluída'),
        (FAILED, 'Falhou'),
    ]
