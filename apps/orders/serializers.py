from rest_framework import serializers
from .models import Order, OrderItem, OrderStatusHistory, Return, ReturnItem


class OrderItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_unit = serializers.CharField(source='product.unit.abbreviation', read_only=True, default='')
    batch_number = serializers.CharField(source='batch.batch_number', read_only=True, default=None)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'category', 'category_name', 'product', 'product_name',
            'product_unit', 'batch', 'batch_number',
            'quantity', 'fulfilled_quantity', 'price', 'total',
            'barcode_scanned',
        ]
        read_only_fields = ['id', 'total']


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = ['id', 'status', 'note', 'created_at']
        read_only_fields = ['id', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'type', 'warehouse', 'warehouse_name',
            'created_by', 'created_by_name', 'customer_name',
            'total_amount', 'note', 'status', 'order_date',
            'items', 'status_history', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'order_number', 'total_amount', 'created_by', 'created_at', 'updated_at']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None


class OrderCreateItemSerializer(serializers.Serializer):
    """Kichik ombor admini buyurtma beradi — faqat kategoriya, mahsulot, miqdor."""
    category = serializers.IntegerField()
    product = serializers.IntegerField()
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2)


class OrderCreateSerializer(serializers.Serializer):
    """Kichik ombor — sodda buyurtma yaratish."""
    note = serializers.CharField(required=False, allow_blank=True, default='')
    items = OrderCreateItemSerializer(many=True)

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.warehouse_id:
            raise serializers.ValidationError(
                {"warehouse": "Sizga ombor biriktirilmagan. Admin bilan bog'laning."}
            )
        return attrs

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user

        order = Order.objects.create(
            type='OUTGOING',
            warehouse_id=user.warehouse_id,
            created_by=user,
            note=validated_data.get('note', ''),
        )

        from apps.products.models import Product
        for item in items_data:
            try:
                product = Product.objects.get(id=item['product'])
            except Product.DoesNotExist:
                continue
            OrderItem.objects.create(
                order=order,
                category_id=item['category'],
                product=product,
                quantity=item['quantity'],
            )

        OrderStatusHistory.objects.create(
            order=order, status='NEW', note='Buyurtma yaratildi'
        )
        return order


class FulfillItemSerializer(serializers.Serializer):
    """Katta ombor admini — partiyadan chiqarish."""
    item_id = serializers.IntegerField()
    batch_id = serializers.IntegerField(required=False, allow_null=True)
    barcode = serializers.CharField(required=False, allow_blank=True, default='')
    fulfilled_quantity = serializers.DecimalField(max_digits=12, decimal_places=2)


class OrderFulfillSerializer(serializers.Serializer):
    """Katta ombor — buyurtmani bajarish."""
    items = FulfillItemSerializer(many=True)
    note = serializers.CharField(required=False, allow_blank=True, default='')


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    note = serializers.CharField(required=False, allow_blank=True, default='')


# ========== RETURN (Vozvrat) ==========

class ReturnItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_unit = serializers.CharField(source='product.unit.abbreviation', read_only=True, default='')
    batch_number = serializers.CharField(source='batch.batch_number', read_only=True, default=None)

    class Meta:
        model = ReturnItem
        fields = ['id', 'product', 'product_name', 'product_unit', 'batch', 'batch_number', 'quantity', 'note']
        read_only_fields = ['id']


class ReturnSerializer(serializers.ModelSerializer):
    items = ReturnItemSerializer(many=True, read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Return
        fields = [
            'id', 'return_number', 'warehouse', 'warehouse_name',
            'created_by', 'created_by_name', 'reason', 'note',
            'status', 'reject_note', 'items', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'return_number', 'created_by', 'created_at', 'updated_at']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None


class ReturnCreateItemSerializer(serializers.Serializer):
    product = serializers.IntegerField()
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    note = serializers.CharField(required=False, allow_blank=True, default='')


class ReturnCreateSerializer(serializers.Serializer):
    reason = serializers.CharField()
    note = serializers.CharField(required=False, allow_blank=True, default='')
    items = ReturnCreateItemSerializer(many=True)

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        ret = Return.objects.create(
            warehouse_id=user.warehouse_id,
            created_by=user,
            reason=validated_data['reason'],
            note=validated_data.get('note', ''),
        )
        from apps.products.models import Product
        for item in items_data:
            ReturnItem.objects.create(
                ret=ret,
                product_id=item['product'],
                quantity=item['quantity'],
                note=item.get('note', ''),
            )
        return ret
