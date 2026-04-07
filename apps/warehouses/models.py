from django.db import models
from django.conf import settings


class Warehouse(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Nomi')
    address = models.TextField(blank=True, verbose_name='Manzil')
    responsible_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='responsible_warehouses',
        verbose_name='Mas\'ul shaxs'
    )
    capacity = models.PositiveIntegerField(default=0, verbose_name='Sig\'imi')
    description = models.TextField(blank=True, verbose_name='Tavsif')
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ombor'
        verbose_name_plural = 'Omborlar'
        ordering = ['name']

    def __str__(self):
        return self.name
