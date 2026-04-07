from rest_framework import serializers
from .models import Warehouse


class WarehouseSerializer(serializers.ModelSerializer):
    responsible_user_name = serializers.SerializerMethodField()

    class Meta:
        model = Warehouse
        fields = [
            'id', 'name', 'address', 'responsible_user',
            'responsible_user_name', 'capacity', 'description',
            'is_active', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_responsible_user_name(self, obj):
        if obj.responsible_user:
            return f"{obj.responsible_user.first_name} {obj.responsible_user.last_name}"
        return None
