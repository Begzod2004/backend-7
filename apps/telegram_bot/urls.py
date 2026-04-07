from django.urls import path
from .views import TelegramConnectView, TelegramStatusView, TelegramDisconnectView

urlpatterns = [
    path('connect/', TelegramConnectView.as_view(), name='telegram-connect'),
    path('status/', TelegramStatusView.as_view(), name='telegram-status'),
    path('disconnect/', TelegramDisconnectView.as_view(), name='telegram-disconnect'),
]
