import json
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from kafka import KafkaConsumer
from fee_api.services import FeeService

logger = logging.getLogger('bankmore')


class Command(BaseCommand):
    help = 'Consume transfer events from Kafka and process fees'

    def handle(self, *args, **options):
        kafka_settings = settings.KAFKA_SETTINGS
        topic = kafka_settings['TOPICS']['TRANSFERS_COMPLETED']
        
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=kafka_settings['BOOTSTRAP_SERVERS'],
            group_id='fee-api-group',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting to consume messages from topic: {topic}')
        )
        
        try:
            for message in consumer:
                try:
                    transfer_data = message.value
                    self.stdout.write(f'Processing transfer: {transfer_data.get("id")}')
                    
                    FeeService.process_transfer_fee(transfer_data)
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully processed fee for transfer: {transfer_data.get("id")}')
                    )
                    
                except Exception as e:
                    logger.error(f'Error processing transfer event: {e}')
                    self.stdout.write(
                        self.style.ERROR(f'Error processing transfer event: {e}')
                    )
                    
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Stopping consumer...'))
        finally:
            consumer.close()
            self.stdout.write(self.style.SUCCESS('Consumer stopped'))
