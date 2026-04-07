from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from core.permissions import IsAdmin, IsAdminOrKattaOmborAdmin
from .models import CustomUser
from .serializers import (
    UserSerializer, UserCreateSerializer,
    UserUpdateSerializer, UserRoleSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.select_related('warehouse').all()
    filterset_fields = ['role', 'is_active', 'warehouse']
    search_fields = ['first_name', 'last_name', 'phone', 'email']
    ordering_fields = ['date_joined', 'first_name']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAdminOrKattaOmborAdmin()]
        return [IsAdmin()]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ('update', 'partial_update'):
            return UserUpdateSerializer
        if self.action == 'set_role':
            return UserRoleSerializer
        return UserSerializer

    @action(detail=True, methods=['put'], url_path='role')
    def set_role(self, request, pk=None):
        user = self.get_object()
        serializer = UserRoleSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(user).data)
