from rest_framework import serializers
from .models import Transfer, TransferItem


class TransferItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    batch_number = serializers.CharField(source='batch.batch_number', read_only=True)

    class Meta:
        model = TransferItem
        fields = [
            'id', 'batch', 'batch_number', 'product', 'product_name',
            'quantity', 'received_quantity', 'note',
        ]
        read_only_fields = ['id']


class TransferSerializer(serializers.ModelSerializer):
    items = TransferItemSerializer(many=True, read_only=True)
    from_warehouse_name = serializers.CharField(source='from_warehouse.name', read_only=True)
    to_warehouse_name = serializers.CharField(source='to_warehouse.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Transfer
        fields = [
            'id', 'transfer_number',
            'from_warehouse', 'from_warehouse_name',
            'to_warehouse', 'to_warehouse_name',
            'created_by', 'created_by_name',
            'driver_name', 'vehicle_number',
            'status', 'note', 'transfer_date',
            'delivered_at', 'items',
            'created_at',
        ]
        read_only_fields = ['id', 'transfer_number', 'created_by', 'created_at']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None


class TransferItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferItem
        fields = ['batch', 'product', 'quantity', 'note']


class TransferCreateSerializer(serializers.ModelSerializer):
    items = TransferItemCreateSerializer(many=True)

    class Meta:
        model = Transfer
        fields = [
            'from_warehouse', 'to_warehouse',
            'driver_name', 'vehicle_number', 'note', 'items',
        ]

    def validate(self, data):
        if data['from_warehouse'] == data['to_warehouse']:
            raise serializers.ValidationError(
                "Qayerdan va qayerga omborlar bir xil bo'lishi mumkin emas."
            )
        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        transfer = Transfer.objects.create(**validated_data)

        for item_data in items_data:
            TransferItem.objects.create(transfer=transfer, **item_data)

        return transfer
