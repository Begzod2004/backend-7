from django.contrib import admin
from .models import Batch, BatchMovement


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('batch_number', 'product', 'warehouse', 'quantity', 'status')
    list_filter = ('status', 'warehouse')
    search_fields = ('batch_number', 'product__name')
    readonly_fields = ('batch_number', 'total_value', 'status')


@admin.register(BatchMovement)
class BatchMovementAdmin(admin.ModelAdmin):
    list_display = ('batch', 'type', 'quantity', 'balance_before', 'balance_after', 'user', 'created_at')
    list_filter = ('type',)
    readonly_fields = ('balance_before', 'balance_after')
