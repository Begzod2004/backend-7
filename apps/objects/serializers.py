from rest_framework import serializers
from .models import ConstructionObject, ObjectMaterial, ObjectExpense


class ObjectMaterialSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)

    class Meta:
        model = ObjectMaterial
        fields = [
            'id', 'object', 'product', 'product_name',
            'planned_quantity', 'used_quantity',
            'unit', 'unit_name', 'note',
        ]
        read_only_fields = ['id']


class ObjectExpenseSerializer(serializers.ModelSerializer):
    batch_number = serializers.CharField(source='batch.batch_number', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    taken_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ObjectExpense
        fields = [
            'id', 'object', 'batch', 'batch_number',
            'quantity', 'price_per_unit', 'total_amount',
            'taken_by', 'taken_by_name',
            'warehouse', 'warehouse_name',
            'note', 'created_at',
        ]
        read_only_fields = ['id', 'total_amount', 'created_at']

    def get_taken_by_name(self, obj):
        if obj.taken_by:
            return f"{obj.taken_by.first_name} {obj.taken_by.last_name}"
        return None


class ConstructionObjectSerializer(serializers.ModelSerializer):
    responsible_user_name = serializers.SerializerMethodField()
    materials = ObjectMaterialSerializer(many=True, read_only=True)
    expenses = ObjectExpenseSerializer(many=True, read_only=True)

    class Meta:
        model = ConstructionObject
        fields = [
            'id', 'name', 'address', 'start_date', 'end_date',
            'responsible_user', 'responsible_user_name',
            'budget', 'status', 'description',
            'materials', 'expenses',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_responsible_user_name(self, obj):
        if obj.responsible_user:
            return f"{obj.responsible_user.first_name} {obj.responsible_user.last_name}"
        return None
