from rest_framework import serializers
from django.db.models import Sum
from .models import Supplier


class SupplierSerializer(serializers.ModelSerializer):
    invoice_count = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'inn', 'phone', 'email', 'address',
            'contact_person', 'rating', 'is_active', 'note',
            'invoice_count', 'total_amount', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_invoice_count(self, obj):
        from apps.invoices.models import ShotInvoice
        return ShotInvoice.objects.filter(supplier_name=obj.name).count()

    def get_total_amount(self, obj):
        from apps.invoices.models import ShotInvoice
        result = ShotInvoice.objects.filter(
            supplier_name=obj.name
        ).aggregate(total=Sum('total_amount'))['total']
        return result or 0
