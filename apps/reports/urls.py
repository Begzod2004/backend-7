from django.urls import path
from .views import (
    InventoryReportView, MovementsReportView,
    LowStockReportView, WarehouseSummaryView,
    ExportExcelView, ExportPDFView,
)
from .charts import DashboardChartsView

urlpatterns = [
    path('inventory/', InventoryReportView.as_view(), name='report-inventory'),
    path('movements/', MovementsReportView.as_view(), name='report-movements'),
    path('low-stock/', LowStockReportView.as_view(), name='report-low-stock'),
    path('warehouse-summary/', WarehouseSummaryView.as_view(), name='report-warehouse-summary'),
    path('export/excel/', ExportExcelView.as_view(), name='report-export-excel'),
    path('export/pdf/', ExportPDFView.as_view(), name='report-export-pdf'),
    path('dashboard/charts/', DashboardChartsView.as_view(), name='dashboard-charts'),
]
