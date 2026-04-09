from django.contrib import admin
from .models import ShotInvoice


@admin.register(ShotInvoice)
class ShotInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'batch', 'warehouse', 'stock_status', 'confirmation_status', 'created_at')
    list_filter = ('warehouse',)
    search_fields = ('invoice_number', 'batch__batch_number')
    readonly_fields = ('invoice_number', 'batch', 'warehouse', 'created_by')
