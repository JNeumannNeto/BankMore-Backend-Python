import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser


class JWTService:
    @staticmethod
    def generate_token(account_data: dict) -> str:
        jwt_settings = settings.JWT_SETTINGS
        
        payload = {
            'account_id': str(account_data['id']),
            'account_number': account_data['number'],
            'cpf': account_data['cpf'],
            'name': account_data['name'],
            'iss': jwt_settings['ISSUER'],
            'aud': jwt_settings['AUDIENCE'],
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=jwt_settings['ACCESS_TOKEN_LIFETIME'])
        }
        
        return jwt.encode(
            payload,
            jwt_settings['SECRET_KEY'],
            algorithm=jwt_settings['ALGORITHM']
        )
    
    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            jwt_settings = settings.JWT_SETTINGS
            
            payload = jwt.decode(
                token,
                jwt_settings['SECRET_KEY'],
                algorithms=[jwt_settings['ALGORITHM']],
                audience=jwt_settings['AUDIENCE'],
                issuer=jwt_settings['ISSUER']
            )
            
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expirado')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Token inválido')


class JWTUser:
    def __init__(self, account_data):
        self.account_id = account_data.get('account_id')
        self.account_number = account_data.get('account_number')
        self.cpf = account_data.get('cpf')
        self.name = account_data.get('name')
        self.is_authenticated = True
        self.is_anonymous = False
    
    def __str__(self):
        return f"JWTUser(account_number={self.account_number}, name={self.name})"


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = JWTService.decode_token(token)
            user = JWTUser(payload)
            return (user, token)
        except AuthenticationFailed:
            return None
    
    def authenticate_header(self, request):
        return 'Bearer'
