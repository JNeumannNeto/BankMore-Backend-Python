from django.db import models
from shared.models import BaseModel
from account_api.models import Account


class Fee(BaseModel):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='fees')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    type = models.CharField(max_length=50, default='TRANSFER')
    description = models.CharField(max_length=255)
    request_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    
    class Meta:
        db_table = 'tarifa'
        verbose_name = 'Tarifa'
        verbose_name_plural = 'Tarifas'
        indexes = [
            models.Index(fields=['account', 'created_at']),
            models.Index(fields=['request_id']),
            models.Index(fields=['type']),
        ]
    
    def __str__(self):
        return f"Fee {self.type} - {self.amount} - Account {self.account.number}"
    
    def save(self, *args, **kwargs):
        if self.amount <= 0:
            raise ValueError("Amount must be positive")
        super().save(*args, **kwargs)
