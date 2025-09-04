import uuid
from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class IdempotencyKey(BaseModel):
    key = models.CharField(max_length=255, unique=True, db_index=True)
    request_data = models.TextField()
    response_data = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, default='PENDING')
    
    class Meta:
        db_table = 'idempotencia'
        verbose_name = 'Chave de Idempotência'
        verbose_name_plural = 'Chaves de Idempotência'

    def __str__(self):
        return f"IdempotencyKey: {self.key}"
