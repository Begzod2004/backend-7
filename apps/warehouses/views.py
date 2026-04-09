import io
from django.http import HttpResponse
from django.db.models import Sum, Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from openpyxl import Workbook
from core.permissions import IsAdmin, IsAdminOrKattaOmborAdmin
from .models import Warehouse
from .serializers import WarehouseSerializer
from apps.batches.models import Batch
from apps.batches.serializers import BatchSerializer


class WarehouseViewSet(viewsets.ModelViewSet):
    serializer_class = WarehouseSerializer
    filterset_fields = ['is_active']
    search_fields = ['name', 'address']
    ordering_fields = ['name', 'created_at']

    def get_queryset(self):
        user = self.request.user
        qs = Warehouse.objects.select_related('responsible_user').all()
        if user.role == 'KICHIK_OMBOR_ADMINI':
            return qs.filter(id=user.warehouse_id)
        return qs

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'inventory', 'inventory_export'):
            return [IsAuthenticated()]
        if self.action == 'destroy':
            return [IsAdmin()]
        return [IsAdminOrKattaOmborAdmin()]

    @action(detail=True, methods=['get'], url_path='inventory')
    def inventory(self, request, pk=None):
        """Ombor inventari — barcha partiyalar."""
        warehouse = self.get_object()
        batches = Batch.objects.filter(warehouse=warehouse).select_related('product', 'unit')
        serializer = BatchSerializer(batches, many=True)

        total_value = batches.aggregate(v=Sum('total_value'))['v'] or 0
        total_batches = batches.count()
        low_count = batches.filter(status='LOW').count()
        empty_count = batches.filter(status='EMPTY').count()

        return Response({
            'warehouse_id': warehouse.id,
            'warehouse_name': warehouse.name,
            'total_batches': total_batches,
            'total_value': float(total_value),
            'low_count': low_count,
            'empty_count': empty_count,
            'batches': serializer.data,
        })

    @action(detail=True, methods=['get'], url_path='inventory/export')
    def inventory_export(self, request, pk=None):
        """Ombor inventarini Excel ga eksport."""
        warehouse = self.get_object()
        batches = Batch.objects.filter(warehouse=warehouse).select_related('product', 'unit')

        wb = Workbook()
        ws = wb.active
        ws.title = f"{warehouse.name} inventari"

        ws.append([
            'Partiya raqami', 'Mahsulot', 'Miqdor', "O'lchov birligi",
            'Narx', 'Umumiy qiymat', 'Min. miqdor', 'Holat', 'Barcode',
        ])

        for b in batches:
            ws.append([
                b.batch_number, b.product.name, float(b.quantity),
                b.unit.abbreviation if b.unit else '',
                float(b.price), float(b.total_value),
                float(b.min_quantity), b.get_status_display(),
                b.barcode or '',
            ])

        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        response = HttpResponse(
            buffer,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{warehouse.name}_inventar.xlsx"'
        return response
