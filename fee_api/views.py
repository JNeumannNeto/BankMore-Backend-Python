from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes
from .serializers import FeeSerializer, FeeListSerializer
from .services import FeeService


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='account_number',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Número da conta'
        )
    ],
    responses={200: FeeListSerializer(many=True)},
    description="Consulta tarifas por número da conta",
    tags=["Fee"]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_fees_by_account_number(request, account_number):
    fees = FeeService.get_fees_by_account_number(account_number)
    serializer = FeeListSerializer(fees, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='fee_id',
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description='ID da tarifa'
        )
    ],
    responses={200: FeeSerializer},
    description="Consulta tarifa específica por ID",
    tags=["Fee"]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_fee_by_id(request, fee_id):
    fee = FeeService.get_fee_by_id(fee_id)
    serializer = FeeSerializer(fee)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    responses={200: FeeListSerializer(many=True)},
    description="Lista as tarifas da conta autenticada",
    tags=["Fee"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_fees(request):
    fees = FeeService.get_fees_by_account_id(request.user.account_id)
    serializer = FeeListSerializer(fees, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
