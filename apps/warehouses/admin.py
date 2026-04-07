from django.contrib import admin
from .models import Warehouse


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'responsible_user', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'address')
