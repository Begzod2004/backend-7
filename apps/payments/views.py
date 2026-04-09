from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsAdmin, IsAdminOrKattaOrHisobchi
from .models import Payment
from .serializers import PaymentSerializer, PaymentCreateSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    filterset_fields = ['invoice', 'supplier', 'payment_method']
    search_fields = ['invoice__invoice_number', 'note']
    ordering_fields = ['created_at', 'amount', 'payment_date']

    def get_queryset(self):
        return Payment.objects.select_related(
            'invoice', 'supplier', 'created_by'
        ).all()

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'debt_summary'):
            return [IsAuthenticated()]
        if self.action == 'destroy':
            return [IsAdmin()]
        return [IsAdminOrKattaOrHisobchi()]

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'], url_path='debt-summary')
    def debt_summary(self, request):
        return Response({
            'total_debt': 0,
            'overdue_debts': 0,
            'per_supplier_debts': [],
        })
