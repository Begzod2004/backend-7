from django.contrib import admin
from .models import ShotInvoice


@admin.register(ShotInvoice)
class ShotInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'supplier_name', 'warehouse', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'warehouse')
    search_fields = ('invoice_number', 'supplier_name', 'document_number')
    readonly_fields = ('invoice_number', 'total_amount')
