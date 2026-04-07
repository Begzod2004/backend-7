from django.contrib import admin
from .models import Estimate, EstimateItem


class EstimateItemInline(admin.TabularInline):
    model = EstimateItem
    extra = 0
    readonly_fields = ('total',)


@admin.register(Estimate)
class EstimateAdmin(admin.ModelAdmin):
    list_display = (
        'estimate_number', 'name', 'object', 'status',
        'total_planned', 'created_by', 'created_at',
    )
    list_filter = ('status',)
    search_fields = ('estimate_number', 'name')
    readonly_fields = ('estimate_number', 'total_planned')
    inlines = [EstimateItemInline]
