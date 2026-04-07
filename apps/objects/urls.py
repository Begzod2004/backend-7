from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConstructionObjectViewSet

router = DefaultRouter()
router.register('', ConstructionObjectViewSet, basename='objects')

urlpatterns = [
    path('', include(router.urls)),
]
