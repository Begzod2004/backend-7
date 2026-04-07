from django.db import models
from django.conf import settings


class Transfer(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Kutilmoqda'),
        ('IN_TRANSIT', "Yo'lda"),
        ('DELIVERED', 'Yetkazildi'),
        ('CANCELLED', 'Bekor qilindi'),
    )
    transfer_number = models.CharField(max_length=20, unique=True, editable=False, verbose_name='Transfer raqami')
    from_warehouse = models.ForeignKey(
        'warehouses.Warehouse', on_delete=models.CASCADE,
        related_name='transfers_from', verbose_name='Qayerdan'
    )
    to_warehouse = models.ForeignKey(
        'warehouses.Warehouse', on_delete=models.CASCADE,
        related_name='transfers_to', verbose_name='Qayerga'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, verbose_name='Yaratuvchi'
    )
    driver_name = models.CharField(max_length=255, blank=True, verbose_name='Haydovchi')
    vehicle_number = models.CharField(max_length=50, blank=True, verbose_name='Mashina raqami')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING', verbose_name='Holat')
    note = models.TextField(blank=True, verbose_name='Izoh')
    transfer_date = models.DateField(auto_now_add=True, verbose_name='Transfer sanasi')
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name='Yetkazilgan vaqt')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Transfer'
        verbose_name_plural = 'Transferlar'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.transfer_number:
            from core.utils import generate_number
            self.transfer_number = generate_number('TRF', Transfer, 'transfer_number')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.transfer_number


class TransferItem(models.Model):
    transfer = models.ForeignKey(
        Transfer, on_delete=models.CASCADE,
        related_name='items', verbose_name='Transfer'
    )
    batch = models.ForeignKey(
        'batches.Batch', on_delete=models.CASCADE,
        verbose_name='Partiya'
    )
    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE,
        verbose_name='Mahsulot'
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Yuborilgan miqdor')
    received_quantity = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        verbose_name='Qabul qilingan miqdor'
    )
    note = models.TextField(blank=True, verbose_name='Izoh')

    class Meta:
        verbose_name = 'Transfer elementi'
        verbose_name_plural = 'Transfer elementlari'

    def __str__(self):
        return f"{self.transfer.transfer_number} — {self.product.name}"
