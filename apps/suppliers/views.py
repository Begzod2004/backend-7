from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count

from core.permissions import IsAdminOrKattaOmborAdmin, IsAdminOrKattaOrHisobchi
from .models import Supplier
from .serializers import SupplierSerializer


class SupplierViewSet(viewsets.ModelViewSet):
    serializer_class = SupplierSerializer
    filterset_fields = ['is_active', 'rating']
    search_fields = ['name', 'inn', 'contact_person', 'phone']
    ordering_fields = ['name', 'rating', 'created_at']

    def get_queryset(self):
        return Supplier.objects.all()

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'invoices', 'stats'):
            return [IsAuthenticated()]
        if self.action == 'destroy':
            return [IsAdminOrKattaOmborAdmin()]
        return [IsAdminOrKattaOrHisobchi()]

    @action(detail=True, methods=['get'], url_path='invoices')
    def invoices(self, request, pk=None):
        supplier = self.get_object()
        from apps.invoices.models import ShotInvoice
        from apps.invoices.serializers import ShotInvoiceSerializer

        invoices = ShotInvoice.objects.filter(
            supplier_name=supplier.name
        ).select_related('batch', 'warehouse', 'created_by').order_by('-created_at')

        serializer = ShotInvoiceSerializer(invoices, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='stats')
    def stats(self, request, pk=None):
        supplier = self.get_object()
        from apps.invoices.models import ShotInvoice

        invoices_qs = ShotInvoice.objects.filter(supplier_name=supplier.name)

        total_invoices = invoices_qs.count()
        total_amount = invoices_qs.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        paid_amount = invoices_qs.filter(status='PAID').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        unpaid_amount = invoices_qs.filter(status='PENDING').aggregate(
            total=Sum('total_amount')
        )['total'] or 0

        top_products = invoices_qs.values(
            'batch__product__name'
        ).annotate(
            total_qty=Sum('quantity'),
            total_sum=Sum('total_amount'),
        ).order_by('-total_sum')[:3]

        top_products_list = [
            {
                'product_name': item['batch__product__name'],
                'total_quantity': item['total_qty'],
                'total_amount': item['total_sum'],
            }
            for item in top_products
        ]

        return Response({
            'total_invoices': total_invoices,
            'total_amount': total_amount,
            'paid_amount': paid_amount,
            'unpaid_amount': unpaid_amount,
            'top_products': top_products_list,
        })
