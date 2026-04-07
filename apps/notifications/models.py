from django.db import models
from django.conf import settings


class Notification(models.Model):
    TYPE_CHOICES = (
        ('LOW_STOCK', 'Kam zaxira'),
        ('EMPTY_STOCK', "Bo'sh zaxira"),
        ('ORDER', 'Buyurtma'),
        ('SYSTEM', 'Tizim'),
    )

    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Turi')
    title = models.CharField(max_length=255, verbose_name='Sarlavha')
    message = models.TextField(verbose_name='Xabar')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True, related_name='notifications',
        verbose_name='Foydalanuvchi'
    )
    is_read = models.BooleanField(default=False, verbose_name="O'qilgan")
    data = models.JSONField(default=dict, blank=True, verbose_name="Qo'shimcha ma'lumot")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Bildirishnoma'
        verbose_name_plural = 'Bildirishnomalar'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.type})"

    @classmethod
    def create_stock_alert(cls, batch):
        if batch.status == 'LOW':
            ntype = 'LOW_STOCK'
            title = 'Kam zaxira ogohlantirishi'
            message = (
                f"{batch.product.name} mahsuloti {batch.warehouse.name} omborida "
                f"kam qoldi. Joriy miqdor: {batch.quantity}"
            )
        elif batch.status == 'EMPTY':
            ntype = 'EMPTY_STOCK'
            title = "Bo'sh zaxira ogohlantirishi"
            message = (
                f"{batch.product.name} mahsuloti {batch.warehouse.name} omborida "
                f"tugadi!"
            )
        else:
            return

        cls.objects.create(
            type=ntype,
            title=title,
            message=message,
            data={
                'batch_id': batch.id,
                'batch_number': batch.batch_number,
                'product_name': batch.product.name,
                'warehouse_name': batch.warehouse.name,
                'quantity': str(batch.quantity),
            }
        )
