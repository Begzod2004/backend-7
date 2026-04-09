from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from apps.reports.dashboard import DashboardStatsView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Auth
    path('api/auth/', include('apps.authentication.urls')),

    # Users
    path('api/users/', include('apps.users.urls')),

    # Categories, Units, Products
    path('api/', include('apps.products.urls')),

    # Warehouses
    path('api/warehouses/', include('apps.warehouses.urls')),

    # Batches & Movements
    path('api/', include('apps.batches.urls')),

    # Invoices
    path('api/invoices/', include('apps.invoices.urls')),

    # Orders
    path('api/orders/', include('apps.orders.urls')),

    # Reports
    path('api/reports/', include('apps.reports.urls')),

    # Notifications
    path('api/notifications/', include('apps.notifications.urls')),

    # Dashboard
    path('api/dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),

    # New modules
    path('api/objects/', include('apps.objects.urls')),
    path('api/suppliers/', include('apps.suppliers.urls')),
    path('api/transfers/', include('apps.transfers.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/estimates/', include('apps.estimates.urls')),
    path('api/returns/', include(('apps.orders.urls_returns', 'returns'))),
    path('api/telegram/', include('apps.telegram_bot.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
