from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(
        source='invoice.invoice_number', read_only=True
    )
    supplier_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id', 'invoice', 'invoice_number', 'supplier', 'supplier_name',
            'amount', 'payment_date', 'payment_method',
            'created_by', 'created_by_name', 'note', 'created_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at']

    def get_supplier_name(self, obj):
        if obj.supplier:
            return obj.supplier.name
        return None

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'invoice', 'supplier', 'amount', 'payment_date',
            'payment_method', 'note',
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("To'lov summasi 0 dan katta bo'lishi kerak.")
        return value
