from rest_framework import serializers
from .models import ShotInvoice


class ShotInvoiceSerializer(serializers.ModelSerializer):
    batch_number = serializers.CharField(source='batch.batch_number', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ShotInvoice
        fields = [
            'id', 'invoice_number', 'batch', 'batch_number',
            'warehouse', 'warehouse_name', 'created_by', 'created_by_name',
            'quantity', 'price', 'total_amount',
            'supplier', 'supplier_name', 'document_date', 'document_number',
            'note', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'invoice_number', 'total_amount', 'created_by', 'created_at', 'updated_at']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None
