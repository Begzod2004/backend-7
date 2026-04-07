from rest_framework import serializers
from .models import Batch, BatchMovement


class BatchSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    unit_abbreviation = serializers.CharField(source='unit.abbreviation', read_only=True)

    class Meta:
        model = Batch
        fields = [
            'id', 'batch_number', 'product', 'product_name',
            'warehouse', 'warehouse_name', 'unit', 'unit_name',
            'unit_abbreviation', 'quantity', 'min_quantity',
            'price', 'total_value', 'description', 'status',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'batch_number', 'total_value', 'status', 'created_at', 'updated_at']


class BatchMovementSerializer(serializers.ModelSerializer):
    batch_number = serializers.CharField(source='batch.batch_number', read_only=True)
    user_name = serializers.SerializerMethodField()
    warehouse_from_name = serializers.CharField(source='warehouse_from.name', read_only=True, default=None)
    warehouse_to_name = serializers.CharField(source='warehouse_to.name', read_only=True, default=None)

    class Meta:
        model = BatchMovement
        fields = [
            'id', 'batch', 'batch_number', 'type', 'quantity',
            'balance_before', 'balance_after', 'user', 'user_name',
            'warehouse_from', 'warehouse_from_name',
            'warehouse_to', 'warehouse_to_name',
            'note', 'created_at',
        ]
        read_only_fields = ['id', 'balance_before', 'balance_after', 'user', 'created_at']

    def get_user_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return None


class BatchMovementCreateSerializer(serializers.Serializer):
    batch = serializers.PrimaryKeyRelatedField(queryset=Batch.objects.all())
    type = serializers.ChoiceField(choices=BatchMovement.TYPE_CHOICES)
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    warehouse_from = serializers.PrimaryKeyRelatedField(
        queryset=Batch.objects.none(), required=False, allow_null=True
    )
    warehouse_to = serializers.PrimaryKeyRelatedField(
        queryset=Batch.objects.none(), required=False, allow_null=True
    )
    note = serializers.CharField(required=False, allow_blank=True, default='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.warehouses.models import Warehouse
        self.fields['warehouse_from'].queryset = Warehouse.objects.all()
        self.fields['warehouse_to'].queryset = Warehouse.objects.all()

    def validate(self, data):
        batch = data['batch']
        if data['type'] == 'OUT' and batch.quantity < data['quantity']:
            raise serializers.ValidationError(
                f"Yetarli miqdor yo'q. Mavjud: {batch.quantity}"
            )
        return data
