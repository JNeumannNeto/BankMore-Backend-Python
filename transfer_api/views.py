from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes
from .serializers import CreateTransferSerializer, TransferSerializer, TransferResponseSerializer
from .services import TransferService


@extend_schema(
    request=CreateTransferSerializer,
    responses={200: TransferResponseSerializer},
    description="Realiza transferência entre contas",
    tags=["Transfer"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_transfer(request):
    serializer = CreateTransferSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    result = TransferService.create_transfer(
        request_id=serializer.validated_data['request_id'],
        origin_account_id=request.user.account_id,
        destination_account_number=serializer.validated_data['destination_account_number'],
        amount=serializer.validated_data['amount']
    )
    
    return Response(result, status=status.HTTP_200_OK)


@extend_schema(
    responses={200: TransferSerializer(many=True)},
    description="Lista as transferências da conta",
    tags=["Transfer"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_transfers(request):
    transfers = TransferService.get_transfers_by_account(request.user.account_id)
    serializer = TransferSerializer(transfers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name='transfer_id',
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description='ID da transferência'
        )
    ],
    responses={200: TransferSerializer},
    description="Consulta uma transferência específica",
    tags=["Transfer"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_transfer(request, transfer_id):
    transfer = TransferService.get_transfer_by_id(transfer_id, request.user.account_id)
    serializer = TransferSerializer(transfer)
    return Response(serializer.data, status=status.HTTP_200_OK)
