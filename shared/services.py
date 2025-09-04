import json
import logging
from typing import Optional, Dict, Any
from django.core.cache import cache
from kafka import KafkaProducer
from django.conf import settings
from .models import IdempotencyKey
from .exceptions import BankMoreException, ErrorTypes

logger = logging.getLogger('bankmore')


class IdempotencyService:
    @staticmethod
    def check_idempotency(key: str, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            idempotency_record = IdempotencyKey.objects.get(key=key)
            
            if idempotency_record.status == 'COMPLETED' and idempotency_record.response_data:
                logger.info(f"Returning cached response for idempotency key: {key}")
                return json.loads(idempotency_record.response_data)
            
            return None
        except IdempotencyKey.DoesNotExist:
            IdempotencyKey.objects.create(
                key=key,
                request_data=json.dumps(request_data),
                status='PENDING'
            )
            return None
    
    @staticmethod
    def save_response(key: str, response_data: Dict[str, Any]):
        try:
            idempotency_record = IdempotencyKey.objects.get(key=key)
            idempotency_record.response_data = json.dumps(response_data)
            idempotency_record.status = 'COMPLETED'
            idempotency_record.save()
        except IdempotencyKey.DoesNotExist:
            logger.error(f"Idempotency key not found: {key}")


class CacheService:
    @staticmethod
    def get(key: str) -> Optional[Any]:
        return cache.get(key)
    
    @staticmethod
    def set(key: str, value: Any, timeout: int = 300):
        cache.set(key, value, timeout)
    
    @staticmethod
    def delete(key: str):
        cache.delete(key)
    
    @staticmethod
    def get_account_balance_key(account_number: str) -> str:
        return f"account_balance:{account_number}"


class KafkaService:
    def __init__(self):
        self.producer = None
        self._initialize_producer()
    
    def _initialize_producer(self):
        try:
            kafka_settings = settings.KAFKA_SETTINGS
            self.producer = KafkaProducer(
                bootstrap_servers=kafka_settings['BOOTSTRAP_SERVERS'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
    
    def send_message(self, topic: str, message: Dict[str, Any], key: Optional[str] = None):
        if not self.producer:
            logger.error("Kafka producer not initialized")
            return
        
        try:
            future = self.producer.send(topic, value=message, key=key)
            future.get(timeout=10)
            logger.info(f"Message sent to topic {topic}: {message}")
        except Exception as e:
            logger.error(f"Failed to send message to Kafka: {e}")
    
    def send_transfer_completed(self, transfer_data: Dict[str, Any]):
        kafka_settings = settings.KAFKA_SETTINGS
        topic = kafka_settings['TOPICS']['TRANSFERS_COMPLETED']
        self.send_message(topic, transfer_data, key=str(transfer_data.get('id')))
    
    def send_fee_charge(self, fee_data: Dict[str, Any]):
        kafka_settings = settings.KAFKA_SETTINGS
        topic = kafka_settings['TOPICS']['FEE_CHARGES']
        self.send_message(topic, fee_data, key=str(fee_data.get('account_number')))
    
    def close(self):
        if self.producer:
            self.producer.close()


kafka_service = KafkaService()
