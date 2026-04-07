from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'type', 'title', 'message', 'user', 'is_read', 'data', 'created_at']
        read_only_fields = ['id', 'type', 'title', 'message', 'data', 'created_at']
