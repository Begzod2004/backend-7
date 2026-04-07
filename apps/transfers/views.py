from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone

from core.permissions import IsAdmin, IsAdminOrKattaOrKichik
from .models import Transfer, TransferItem
from .serializers import TransferSerializer, TransferCreateSerializer


class TransferViewSet(viewsets.ModelViewSet):
    serializer_class = TransferSerializer
    filterset_fields = ['status', 'from_warehouse', 'to_warehouse']
    search_fields = ['transfer_number', 'driver_name', 'vehicle_number']
    ordering_fields = ['created_at', 'transfer_date']

    def get_queryset(self):
        user = self.request.user
        qs = Transfer.objects.select_related(
            'from_warehouse', 'to_warehouse', 'created_by'
        ).prefetch_related(
            'items__batch', 'items__product'
        ).all()

        if user.role == 'KICHIK_OMBOR_ADMINI':
            return qs.filter(
                Q(from_warehouse_id=user.warehouse_id) |
                Q(to_warehouse_id=user.warehouse_id)
            )
        return qs

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        if self.action == 'destroy':
            return [IsAdmin()]
        return [IsAdminOrKattaOrKichik()]

    def get_serializer_class(self):
        if self.action == 'create':
            return TransferCreateSerializer
        return TransferSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['put'], url_path='deliver')
    def deliver(self, request, pk=None):
        transfer = self.get_object()

        if transfer.status == 'DELIVERED':
            return Response(
                {'error': 'Bu transfer allaqachon yetkazilgan.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if transfer.status == 'CANCELLED':
            return Response(
                {'error': 'Bekor qilingan transferni yetkazish mumkin emas.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from apps.batches.models import Batch

        user = request.user

        for item in transfer.items.select_related('batch', 'product').all():
            source_batch = item.batch
            received_qty = item.received_quantity if item.received_quantity is not None else item.quantity

            # OUT from source warehouse batch
            source_batch.update_quantity(
                amount=item.quantity,
                movement_type='OUT',
                user=user,
                warehouse_from=transfer.from_warehouse,
                warehouse_to=transfer.to_warehouse,
                note=f"Transfer {transfer.transfer_number} — chiqim",
            )

            # Find or create batch in destination warehouse
            dest_batch = Batch.objects.filter(
                product=item.product,
                warehouse=transfer.to_warehouse,
            ).first()

            if dest_batch:
                dest_batch.update_quantity(
                    amount=received_qty,
                    movement_type='IN',
                    user=user,
                    warehouse_from=transfer.from_warehouse,
                    warehouse_to=transfer.to_warehouse,
                    note=f"Transfer {transfer.transfer_number} — kirim",
                )
            else:
                dest_batch = Batch(
                    product=item.product,
                    warehouse=transfer.to_warehouse,
                    unit=source_batch.unit,
                    quantity=received_qty,
                    min_quantity=source_batch.min_quantity,
                    price=source_batch.price,
                    description=f"Transfer {transfer.transfer_number} orqali yaratildi",
                )
                dest_batch.save()

                from apps.batches.models import BatchMovement
                BatchMovement.objects.create(
                    batch=dest_batch,
                    type='IN',
                    quantity=received_qty,
                    balance_before=0,
                    balance_after=received_qty,
                    user=user,
                    warehouse_from=transfer.from_warehouse,
                    warehouse_to=transfer.to_warehouse,
                    note=f"Transfer {transfer.transfer_number} — yangi partiya kirim",
                )

        transfer.status = 'DELIVERED'
        transfer.delivered_at = timezone.now()
        transfer.save(update_fields=['status', 'delivered_at'])

        return Response(TransferSerializer(transfer).data)
