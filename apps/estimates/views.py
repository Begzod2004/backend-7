from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from core.permissions import IsAdmin, IsAdminOrKattaOrHisobchi
from .models import Estimate
from .serializers import EstimateSerializer, EstimateCreateSerializer


class EstimateViewSet(viewsets.ModelViewSet):
    serializer_class = EstimateSerializer
    filterset_fields = ['status', 'object']
    search_fields = ['estimate_number', 'name']
    ordering_fields = ['created_at', 'total_planned']

    def get_queryset(self):
        return Estimate.objects.select_related(
            'object', 'created_by', 'approved_by'
        ).prefetch_related(
            'items__product', 'items__unit'
        ).all()

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'compare'):
            return [IsAuthenticated()]
        if self.action == 'destroy':
            return [IsAdmin()]
        if self.action == 'approve':
            return [IsAdmin()]
        return [IsAdminOrKattaOrHisobchi()]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return EstimateCreateSerializer
        return EstimateSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_destroy(self, instance):
        if instance.status != 'DRAFT':
            raise ValidationError(
                "Faqat 'Qoralama' holatidagi smetalarni o'chirish mumkin."
            )
        instance.delete()

    @action(detail=True, methods=['put'], url_path='approve')
    def approve(self, request, pk=None):
        """Approve an estimate. Sets status to APPROVED and records approved_by."""
        estimate = self.get_object()
        if estimate.status != 'DRAFT':
            return Response(
                {'detail': "Faqat 'Qoralama' holatidagi smetalarni tasdiqlash mumkin."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        estimate.status = 'APPROVED'
        estimate.approved_by = request.user
        estimate.save(update_fields=['status', 'approved_by', 'updated_at'])
        return Response(EstimateSerializer(estimate).data)

    @action(detail=True, methods=['get'], url_path='compare')
    def compare(self, request, pk=None):
        """
        Compare estimate items with actual object expenses.
        For each EstimateItem, find matching ObjectExpense quantities
        and return planned_qty, used_qty, difference.
        """
        estimate = self.get_object()
        comparison = []

        for item in estimate.items.select_related('product', 'unit').all():
            planned_qty = item.quantity

            # Try to find matching ObjectExpense records for this product
            # in the same construction object
            used_qty = 0
            if estimate.object:
                try:
                    from apps.objects.models import ObjectExpense
                    expenses = ObjectExpense.objects.filter(
                        object=estimate.object,
                        product=item.product,
                    )
                    from django.db.models import Sum
                    used_qty = expenses.aggregate(
                        total=Sum('quantity')
                    )['total'] or 0
                except (ImportError, Exception):
                    used_qty = 0

            difference = planned_qty - used_qty

            comparison.append({
                'product_id': item.product_id,
                'product_name': item.product.name,
                'unit': item.unit.abbreviation,
                'planned_qty': planned_qty,
                'used_qty': used_qty,
                'difference': difference,
                'price_per_unit': item.price_per_unit,
                'planned_total': item.total,
            })

        return Response({
            'estimate_number': estimate.estimate_number,
            'estimate_name': estimate.name,
            'object_name': estimate.object.name if estimate.object else None,
            'items': comparison,
        })
