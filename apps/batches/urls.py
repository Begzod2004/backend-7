from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BatchViewSet, BatchMovementViewSet

router = DefaultRouter()
router.register('batches', BatchViewSet, basename='batches')
router.register('movements', BatchMovementViewSet, basename='movements')

urlpatterns = [
    path('', include(router.urls)),
]
