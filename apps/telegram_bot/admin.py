from django.contrib import admin
from .models import TelegramUser


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'telegram_chat_id', 'is_active', 'connected_at')
    list_filter = ('is_active',)
    search_fields = ('user__first_name', 'user__last_name', 'telegram_chat_id')
    raw_id_fields = ('user',)
