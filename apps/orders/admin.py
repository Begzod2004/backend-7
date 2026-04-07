from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total',)


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'type', 'warehouse', 'status', 'total_amount', 'created_at')
    list_filter = ('type', 'status', 'warehouse')
    search_fields = ('order_number', 'customer_name')
    readonly_fields = ('order_number', 'total_amount')
    inlines = [OrderItemInline, OrderStatusHistoryInline]
