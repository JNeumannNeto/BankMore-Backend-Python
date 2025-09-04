from django.db import models
from shared.models import BaseModel
from shared.utils import TransferStatus
from account_api.models import Account


class Transfer(BaseModel):
    origin_account = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        related_name='transfers_sent'
    )
    destination_account = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        related_name='transfers_received'
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.IntegerField(choices=TransferStatus.CHOICES, default=TransferStatus.PENDING)
    description = models.CharField(max_length=255, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    idempotency_key = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    
    class Meta:
        db_table = 'transferencia'
        verbose_name = 'Transferência'
        verbose_name_plural = 'Transferências'
        indexes = [
            models.Index(fields=['origin_account', 'created_at']),
            models.Index(fields=['destination_account', 'created_at']),
            models.Index(fields=['idempotency_key']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Transfer {self.amount} from {self.origin_account.number} to {self.destination_account.number}"
    
    def save(self, *args, **kwargs):
        if self.amount <= 0:
            raise ValueError("Amount must be positive")
        super().save(*args, **kwargs)
    
    def mark_completed(self):
        from django.utils import timezone
        self.status = TransferStatus.COMPLETED
        self.completed_at = timezone.now()
        self.save()
    
    def mark_failed(self):
        self.status = TransferStatus.FAILED
        self.save()
