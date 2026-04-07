from django.db import models
from django.conf import settings


class TelegramUser(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='telegram', verbose_name='Foydalanuvchi'
    )
    telegram_chat_id = models.BigIntegerField(
        unique=True, verbose_name='Telegram Chat ID'
    )
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    connected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Telegram foydalanuvchi'
        verbose_name_plural = 'Telegram foydalanuvchilar'

    def __str__(self):
        return f"{self.user} — {self.telegram_chat_id}"
