from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

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
        if self.action in ('list', 'retrieve', 'stats'):
            return [IsAuthenticated()]
        if self.action == 'destroy':
            return [IsAdminOrKattaOmborAdmin()]
        return [IsAdminOrKattaOrHisobchi()]

    @action(detail=True, methods=['get'], url_path='stats')
    def stats(self, request, pk=None):
        supplier = self.get_object()
        return Response({
            'total_invoices': 0,
            'total_amount': 0,
            'paid_amount': 0,
            'unpaid_amount': 0,
            'top_products': [],
        })
