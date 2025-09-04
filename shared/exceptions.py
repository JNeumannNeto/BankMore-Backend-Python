from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


class BankMoreException(Exception):
    def __init__(self, message, error_type, status_code=status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        super().__init__(self.message)


class ErrorTypes:
    INVALID_DOCUMENT = "INVALID_DOCUMENT"
    USER_UNAUTHORIZED = "USER_UNAUTHORIZED"
    INVALID_ACCOUNT = "INVALID_ACCOUNT"
    INACTIVE_ACCOUNT = "INACTIVE_ACCOUNT"
    INVALID_VALUE = "INVALID_VALUE"
    INVALID_TYPE = "INVALID_TYPE"
    INSUFFICIENT_BALANCE = "INSUFFICIENT_BALANCE"
    INVALID_AMOUNT = "INVALID_AMOUNT"
    INVALID_TRANSFER = "INVALID_TRANSFER"
    ACCOUNT_NOT_FOUND = "ACCOUNT_NOT_FOUND"
    INVALID_OPERATION = "INVALID_OPERATION"
    INVALID_ARGUMENT = "INVALID_ARGUMENT"
    INTERNAL_ERROR = "INTERNAL_ERROR"


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if isinstance(exc, BankMoreException):
        custom_response_data = {
            'message': exc.message,
            'type': exc.error_type
        }
        return Response(custom_response_data, status=exc.status_code)
    
    if response is not None:
        custom_response_data = {
            'message': 'Erro interno do servidor',
            'type': ErrorTypes.INTERNAL_ERROR
        }
        
        if hasattr(response, 'data'):
            if isinstance(response.data, dict):
                if 'detail' in response.data:
                    custom_response_data['message'] = str(response.data['detail'])
                elif 'non_field_errors' in response.data:
                    custom_response_data['message'] = str(response.data['non_field_errors'][0])
                else:
                    first_error = next(iter(response.data.values()))
                    if isinstance(first_error, list):
                        custom_response_data['message'] = str(first_error[0])
                    else:
                        custom_response_data['message'] = str(first_error)
        
        response.data = custom_response_data
    
    return response
