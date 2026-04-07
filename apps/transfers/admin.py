from django.contrib import admin
from .models import Transfer, TransferItem


class TransferItemInline(admin.TabularInline):
    model = TransferItem
    extra = 0


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ('transfer_number', 'from_warehouse', 'to_warehouse', 'status', 'driver_name', 'transfer_date', 'delivered_at', 'created_at')
    list_filter = ('status', 'from_warehouse', 'to_warehouse')
    search_fields = ('transfer_number', 'driver_name', 'vehicle_number')
    readonly_fields = ('transfer_number',)
    inlines = [TransferItemInline]


@admin.register(TransferItem)
class TransferItemAdmin(admin.ModelAdmin):
    list_display = ('transfer', 'product', 'batch', 'quantity', 'received_quantity')
    list_filter = ('transfer',)
    search_fields = ('product__name', 'transfer__transfer_number')
