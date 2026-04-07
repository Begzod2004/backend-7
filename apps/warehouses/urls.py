from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WarehouseViewSet

router = DefaultRouter()
router.register('', WarehouseViewSet, basename='warehouses')

urlpatterns = [
    path('', include(router.urls)),
]
