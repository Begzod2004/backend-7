from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShotInvoiceViewSet

router = DefaultRouter()
router.register('', ShotInvoiceViewSet, basename='invoices')

urlpatterns = [
    path('', include(router.urls)),
]
