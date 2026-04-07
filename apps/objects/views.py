from decimal import Decimal

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum

from core.permissions import IsAdmin, IsAdminOrKattaOmborAdmin
from .models import ConstructionObject, ObjectMaterial, ObjectExpense
from .serializers import (
    ConstructionObjectSerializer,
    ObjectMaterialSerializer,
    ObjectExpenseSerializer,
)


class ConstructionObjectViewSet(viewsets.ModelViewSet):
    serializer_class = ConstructionObjectSerializer
    filterset_fields = ['status']
    search_fields = ['name', 'address']
    ordering_fields = ['created_at', 'budget', 'name']

    def get_queryset(self):
        return ConstructionObject.objects.select_related(
            'responsible_user'
        ).prefetch_related(
            'materials__product', 'materials__unit',
            'expenses__batch', 'expenses__warehouse', 'expenses__taken_by',
        ).all()

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'materials', 'expenses', 'summary'):
            return [IsAuthenticated()]
        if self.action == 'destroy':
            return [IsAdmin()]
        return [IsAdminOrKattaOmborAdmin()]

    @action(detail=True, methods=['get', 'post'], url_path='materials')
    def materials(self, request, pk=None):
        obj = self.get_object()

        if request.method == 'GET':
            materials = obj.materials.select_related('product', 'unit').all()
            serializer = ObjectMaterialSerializer(materials, many=True)
            return Response(serializer.data)

        serializer = ObjectMaterialSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(object=obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'], url_path='expenses')
    def expenses(self, request, pk=None):
        obj = self.get_object()

        if request.method == 'GET':
            expenses = obj.expenses.select_related(
                'batch', 'warehouse', 'taken_by'
            ).all()
            serializer = ObjectExpenseSerializer(expenses, many=True)
            return Response(serializer.data)

        serializer = ObjectExpenseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(object=obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='summary')
    def summary(self, request, pk=None):
        obj = self.get_object()

        total_spent = obj.expenses.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')

        materials_breakdown = []
        for material in obj.materials.select_related('product', 'unit').all():
            materials_breakdown.append({
                'product_id': material.product_id,
                'product_name': material.product.name,
                'unit_name': material.unit.name,
                'planned_quantity': material.planned_quantity,
                'used_quantity': material.used_quantity,
                'difference': material.planned_quantity - material.used_quantity,
            })

        return Response({
            'budget': obj.budget,
            'total_spent': total_spent,
            'budget_difference': obj.budget - total_spent,
            'materials_breakdown': materials_breakdown,
        })
