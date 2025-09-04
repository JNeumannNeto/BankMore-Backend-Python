from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes
from .serializers import (
    CreateAccountSerializer, LoginSerializer, CreateMovementSerializer,
    DeactivateAccountSerializer, BalanceSerializer, CreateAccountResponseSerializer,
    LoginResponseSerializer
)
from .services import AccountService


@extend_schema(
    request=CreateAccountSerializer,
    responses={200: CreateAccountResponseSerializer},
    description="Cadastra uma nova conta corrente",
    tags=["Account"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = CreateAccountSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    result = AccountService.create_account(
        cpf=serializer.validated_data['cpf'],
        name=serializer.validated_data['name'],
        password=serializer.validated_data['password']
    )
    
    return Response(result, status=status.HTTP_200_OK)


@extend_schema(
    request=LoginSerializer,
    responses={200: LoginResponseSerializer},
    description="Realiza login na conta corrente",
    tags=["Account"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    result = AccountService.authenticate(
        cpf=serializer.validated_data['cpf'],
        password=serializer.validated_data['password']
    )
    
    return Response(result, status=status.HTTP_200_OK)


@extend_schema(
    request=DeactivateAccountSerializer,
    responses={204: None},
    description="Inativa a conta corrente",
    tags=["Account"]
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def deactivate(request):
    serializer = DeactivateAccountSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    AccountService.deactivate_account(
        account_id=request.user.account_id,
        password=serializer.validated_data['password']
    )
    
    return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    request=CreateMovementSerializer,
    responses={204: None},
    description="Realiza movimentação na conta corrente",
    tags=["Account"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def movement(request):
    serializer = CreateMovementSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    AccountService.create_movement(
        request_id=serializer.validated_data['request_id'],
        account_number=serializer.validated_data['account_number'],
        amount=serializer.validated_data['amount'],
        movement_type=serializer.validated_data['type'],
        user_account_id=request.user.account_id
    )
    
    return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    responses={200: BalanceSerializer},
    description="Consulta o saldo da conta corrente",
    tags=["Account"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def balance(request):
    result = AccountService.get_balance(request.user.account_id)
    return Response(result, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='account_number',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Número da conta'
        )
    ],
    responses={200: OpenApiTypes.BOOL},
    description="Verifica se uma conta existe pelo número",
    tags=["Account"]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def account_exists(request, account_number):
    exists = AccountService.account_exists(account_number)
    return Response(exists, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='account_number',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Número da conta'
        )
    ],
    responses={200: BalanceSerializer},
    description="Consulta o saldo de uma conta pelo número",
    tags=["Account"]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def balance_by_account_number(request, account_number):
    result = AccountService.get_balance_by_account_number(account_number)
    return Response(result, status=status.HTTP_200_OK)
