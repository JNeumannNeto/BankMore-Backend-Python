import logging
import json
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from .exceptions import BankMoreException, ErrorTypes

logger = logging.getLogger('bankmore')


class GlobalExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, BankMoreException):
            logger.warning(f"BankMore Exception: {exception.error_type} - {exception.message}")
            return JsonResponse({
                'message': exception.message,
                'type': exception.error_type
            }, status=exception.status_code)
        
        logger.error(f"Unhandled exception: {str(exception)}", exc_info=True)
        return JsonResponse({
            'message': 'Erro interno do servidor',
            'type': ErrorTypes.INTERNAL_ERROR
        }, status=500)


class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        logger.info(f"Request: {request.method} {request.path}")
        return None
    
    def process_response(self, request, response):
        logger.info(f"Response: {request.method} {request.path} - {response.status_code}")
        return response
