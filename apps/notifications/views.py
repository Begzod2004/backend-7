from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    filterset_fields = ['type', 'is_read']
    ordering_fields = ['created_at']

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.filter(
            models.Q(user=user) | models.Q(user__isnull=True)
        )

    @action(detail=True, methods=['put'], url_path='read')
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=['put'], url_path='read-all')
    def mark_all_read(self, request):
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({'detail': 'Barcha bildirishnomalar o\'qilgan deb belgilandi'})
