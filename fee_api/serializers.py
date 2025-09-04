from rest_framework import serializers
from .models import Fee


class FeeSerializer(serializers.ModelSerializer):
    account_number = serializers.CharField(source='account.number', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)
    
    class Meta:
        model = Fee
        fields = [
            'id', 'amount', 'type', 'description', 'request_id',
            'account_number', 'account_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class FeeListSerializer(serializers.ModelSerializer):
    account_number = serializers.CharField(source='account.number', read_only=True)
    
    class Meta:
        model = Fee
        fields = [
            'id', 'amount', 'type', 'description', 
            'account_number', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
