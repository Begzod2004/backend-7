from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsAdminOrKattaOrKichik, IsAdminOrKattaOrHisobchi
from .models import Batch, BatchMovement
from .serializers import (
    BatchSerializer, BatchMovementSerializer, BatchMovementCreateSerializer,
)


class BatchViewSet(viewsets.ModelViewSet):
    serializer_class = BatchSerializer
    filterset_fields = ['product', 'warehouse', 'status']
    search_fields = ['batch_number', 'product__name']
    ordering_fields = ['created_at', 'quantity', 'price']

    def get_queryset(self):
        user = self.request.user
        qs = Batch.objects.select_related('product', 'warehouse', 'unit').all()
        if user.role == 'KICHIK_OMBOR_ADMINI':
            return qs.filter(warehouse_id=user.warehouse_id)
        return qs

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'movements'):
            return [IsAuthenticated()]
        return [IsAdminOrKattaOrKichik()]

    def perform_create(self, serializer):
        user = self.request.user
        # Agar warehouse berilmagan bo'lsa, asosiy omborni ishlatamiz
        from apps.warehouses.models import Warehouse
        if not serializer.validated_data.get('warehouse'):
            main_wh = Warehouse.objects.filter(is_main=True).first() or Warehouse.objects.first()
            if main_wh:
                serializer.validated_data['warehouse'] = main_wh

        # invoice_number ni ajratib olamiz (BatchSerializer ga kirmaydi)
        invoice_number = self.request.data.get('invoice_number', '').strip()

        batch = serializer.save()
        if user.role == 'KICHIK_OMBOR_ADMINI' and batch.warehouse_id != user.warehouse_id:
            batch.delete()
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Faqat o'z omboringizga partiya qo'sha olasiz")
        if batch.quantity > 0:
            from apps.batches.models import BatchMovement
            BatchMovement.objects.create(
                batch=batch, type='IN', quantity=batch.quantity,
                balance_before=0, balance_after=batch.quantity,
                user=user, warehouse_to=batch.warehouse,
                note='Yangi partiya yaratildi',
            )

        # Shot-faktura avtomatik yaratish
        if invoice_number:
            from apps.invoices.models import ShotInvoice
            ShotInvoice.objects.create(
                invoice_number=invoice_number,
                batch=batch,
                warehouse=batch.warehouse,
                created_by=user,
            )

    @action(detail=True, methods=['get'], url_path='movements')
    def movements(self, request, pk=None):
        batch = self.get_object()
        movements = batch.movements.select_related('user', 'warehouse_from', 'warehouse_to').all()
        serializer = BatchMovementSerializer(movements, many=True)
        return Response(serializer.data)


class BatchMovementViewSet(viewsets.ModelViewSet):
    serializer_class = BatchMovementSerializer
    filterset_fields = ['batch', 'type', 'warehouse_from', 'warehouse_to']
    ordering_fields = ['created_at']
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        qs = BatchMovement.objects.select_related(
            'batch', 'user', 'warehouse_from', 'warehouse_to'
        ).all()
        if user.role == 'KICHIK_OMBOR_ADMINI':
            qs = qs.filter(batch__warehouse_id=user.warehouse_id)
        return qs

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated()]
        return [IsAdminOrKattaOrKichik()]

    def get_serializer_class(self):
        if self.action == 'create':
            return BatchMovementCreateSerializer
        return BatchMovementSerializer

    def create(self, request, *args, **kwargs):
        serializer = BatchMovementCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        batch = data['batch']

        user = request.user
        if user.role == 'KICHIK_OMBOR_ADMINI' and batch.warehouse_id != user.warehouse_id:
            return Response(
                {'error': "Faqat o'z omboringizdagi partiyalarni boshqara olasiz"},
                status=status.HTTP_403_FORBIDDEN
            )

        batch.update_quantity(
            data['quantity'], data['type'], user,
            warehouse_from=data.get('warehouse_from'),
            warehouse_to=data.get('warehouse_to'),
            note=data.get('note', ''),
        )

        return Response(
            BatchSerializer(batch).data,
            status=status.HTTP_201_CREATED
        )
