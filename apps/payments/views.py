from decimal import Decimal
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsAdmin, IsAdminOrKattaOrHisobchi
from apps.invoices.models import ShotInvoice
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
        total_debt = Decimal('0')
        overdue_debt = Decimal('0')
        supplier_debts = {}
        thirty_days_ago = timezone.now().date() - timedelta(days=30)

        for inv in ShotInvoice.objects.filter(status='PENDING'):
            paid = inv.payments.aggregate(s=Sum('amount'))['s'] or Decimal('0')
            debt = inv.total_amount - paid
            if debt <= 0:
                continue
            total_debt += debt
            if inv.document_date < thirty_days_ago:
                overdue_debt += debt
            name = inv.supplier_name
            supplier_debts[name] = supplier_debts.get(name, Decimal('0')) + debt

        per_supplier = [
            {'supplier_name': k, 'supplier_debt': float(v)}
            for k, v in sorted(supplier_debts.items(), key=lambda x: -x[1])
        ]

        return Response({
            'total_debt': float(total_debt),
            'overdue_debts': float(overdue_debt),
            'per_supplier_debts': per_supplier,
        })
