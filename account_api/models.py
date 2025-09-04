from django.db import models
from decimal import Decimal
from shared.models import BaseModel
from shared.utils import MovementTypes, AccountNumberGenerator, PasswordHasher


class Account(BaseModel):
    number = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    cpf = models.CharField(max_length=11, unique=True, db_index=True)
    active = models.BooleanField(default=True)
    password_hash = models.CharField(max_length=100)
    salt = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'contacorrente'
        verbose_name = 'Conta Corrente'
        verbose_name_plural = 'Contas Correntes'
        indexes = [
            models.Index(fields=['number']),
            models.Index(fields=['cpf']),
        ]
    
    def __str__(self):
        return f"Account {self.number} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.number:
            self.number = AccountNumberGenerator.generate()
        super().save(*args, **kwargs)
    
    def deactivate(self):
        self.active = False
        self.save()
    
    def activate(self):
        self.active = True
        self.save()
    
    def verify_password(self, password: str) -> bool:
        return PasswordHasher.verify_password(password, self.salt, self.password_hash)
    
    def get_balance(self) -> Decimal:
        credits = self.movements.filter(type=MovementTypes.CREDIT).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0')
        
        debits = self.movements.filter(type=MovementTypes.DEBIT).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0')
        
        return credits - debits


class Movement(BaseModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='movements')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    type = models.CharField(max_length=1, choices=MovementTypes.CHOICES)
    description = models.CharField(max_length=255, blank=True)
    idempotency_key = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    
    class Meta:
        db_table = 'movimento'
        verbose_name = 'Movimento'
        verbose_name_plural = 'Movimentos'
        indexes = [
            models.Index(fields=['account', 'created_at']),
            models.Index(fields=['idempotency_key']),
        ]
    
    def __str__(self):
        return f"Movement {self.type} - {self.amount} - Account {self.account.number}"
    
    def save(self, *args, **kwargs):
        if self.amount <= 0:
            raise ValueError("Amount must be positive")
        super().save(*args, **kwargs)
