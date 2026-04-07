from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsAdminOrKattaOmborAdmin, IsAdminOrKattaOrKichik
from .models import Order, OrderStatusHistory
from .serializers import (
    OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer,
)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    filterset_fields = ['type', 'warehouse', 'status']
    search_fields = ['order_number', 'customer_name']
    ordering_fields = ['created_at', 'total_amount', 'order_date']

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.select_related('warehouse', 'created_by').prefetch_related(
            'items__product', 'items__batch', 'status_history'
        ).all()
        if user.role == 'KICHIK_OMBOR_ADMINI':
            return qs.filter(warehouse_id=user.warehouse_id)
        return qs

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        if self.action in ('destroy', 'update_status'):
            return [IsAdminOrKattaOmborAdmin()]
        return [IsAdminOrKattaOrKichik()]

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        if self.action == 'update_status':
            return OrderStatusUpdateSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        user = self.request.user
        order = serializer.save(created_by=user)
        if user.role == 'KICHIK_OMBOR_ADMINI' and order.warehouse_id != user.warehouse_id:
            order.delete()
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Faqat o'z omboringizdan buyurtma bera olasiz")

    @action(detail=True, methods=['put'], url_path='status')
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['status']
        note = serializer.validated_data.get('note', '')

        order.status = new_status
        order.save(update_fields=['status', 'updated_at'])

        OrderStatusHistory.objects.create(
            order=order, status=new_status, note=note
        )

        return Response(OrderSerializer(order).data)
