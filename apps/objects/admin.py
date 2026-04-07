from django.contrib import admin
from .models import ConstructionObject, ObjectMaterial, ObjectExpense


class ObjectMaterialInline(admin.TabularInline):
    model = ObjectMaterial
    extra = 0


class ObjectExpenseInline(admin.TabularInline):
    model = ObjectExpense
    extra = 0
    readonly_fields = ('total_amount',)


@admin.register(ConstructionObject)
class ConstructionObjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'budget', 'responsible_user', 'start_date', 'end_date', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'address')
    inlines = [ObjectMaterialInline, ObjectExpenseInline]


@admin.register(ObjectMaterial)
class ObjectMaterialAdmin(admin.ModelAdmin):
    list_display = ('object', 'product', 'planned_quantity', 'used_quantity', 'unit')
    list_filter = ('object',)
    search_fields = ('product__name',)


@admin.register(ObjectExpense)
class ObjectExpenseAdmin(admin.ModelAdmin):
    list_display = ('object', 'batch', 'quantity', 'price_per_unit', 'total_amount', 'warehouse', 'created_at')
    list_filter = ('object', 'warehouse')
    readonly_fields = ('total_amount',)
