from rest_framework import serializers
from .models import ShotInvoice


class ShotInvoiceSerializer(serializers.ModelSerializer):
    batch_number = serializers.CharField(source='batch.batch_number', read_only=True)
    product_name = serializers.CharField(source='batch.product.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    stock_status = serializers.CharField(read_only=True)
    confirmation_status = serializers.CharField(read_only=True)
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()

    class Meta:
        model = ShotInvoice
        fields = [
            'id', 'invoice_number', 'batch', 'batch_number', 'product_name',
            'warehouse', 'warehouse_name', 'created_by', 'created_by_name',
            'file', 'file_url', 'file_name',
            'stock_status', 'confirmation_status',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'invoice_number', 'batch', 'warehouse',
            'created_by', 'created_at', 'updated_at',
        ]

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    def get_file_name(self, obj):
        if obj.file:
            return obj.file.name.split('/')[-1]
        return None
