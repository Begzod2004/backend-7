from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsAdmin, IsAdminOrKattaOmborAdmin
from .models import Warehouse
from .serializers import WarehouseSerializer


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
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        if self.action == 'destroy':
            return [IsAdmin()]
        return [IsAdminOrKattaOmborAdmin()]
