from django.db import models
from django.conf import settings
from core.utils import generate_number


class Batch(models.Model):
    STATUS_CHOICES = (
        ('NORMAL', 'Normal'),
        ('LOW', 'Kam'),
        ('EMPTY', "Bo'sh"),
    )

    batch_number = models.CharField(max_length=20, unique=True, editable=False, verbose_name='Partiya raqami')
    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE,
        related_name='batches', verbose_name='Mahsulot'
    )
    warehouse = models.ForeignKey(
        'warehouses.Warehouse', on_delete=models.CASCADE,
        related_name='batches', verbose_name='Ombor'
    )
    unit = models.ForeignKey(
        'products.Unit', on_delete=models.PROTECT,
        related_name='batches', verbose_name="O'lchov birligi"
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Miqdor')
    min_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Minimal miqdor')
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Narx')
    total_value = models.DecimalField(max_digits=18, decimal_places=2, default=0, editable=False, verbose_name='Umumiy qiymat')
    description = models.TextField(blank=True, verbose_name='Tavsif')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='NORMAL', verbose_name='Holat')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Partiya'
        verbose_name_plural = 'Partiyalar'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.batch_number} - {self.product.name}"

    def save(self, *args, **kwargs):
        if not self.batch_number:
            self.batch_number = generate_number('BATCH', Batch, 'batch_number')
        self.total_value = self.quantity * self.price
        if self.quantity <= 0:
            self.status = 'EMPTY'
        elif self.quantity <= self.min_quantity:
            self.status = 'LOW'
        else:
            self.status = 'NORMAL'
        super().save(*args, **kwargs)

    def update_quantity(self, amount, movement_type, user, warehouse_from=None, warehouse_to=None, note=''):
        balance_before = self.quantity
        if movement_type == 'IN':
            self.quantity += amount
        elif movement_type == 'OUT':
            self.quantity -= amount
        elif movement_type == 'ADJUSTMENT':
            self.quantity = amount
        self.save()

        BatchMovement.objects.create(
            batch=self,
            type=movement_type,
            quantity=amount,
            balance_before=balance_before,
            balance_after=self.quantity,
            user=user,
            warehouse_from=warehouse_from,
            warehouse_to=warehouse_to,
            note=note,
        )

        if self.status in ('LOW', 'EMPTY'):
            from apps.notifications.models import Notification
            Notification.create_stock_alert(self)


class BatchMovement(models.Model):
    TYPE_CHOICES = (
        ('IN', 'Kirim'),
        ('OUT', 'Chiqim'),
        ('ADJUSTMENT', 'Tuzatish'),
    )

    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='movements', verbose_name='Partiya')
    type = models.CharField(max_length=15, choices=TYPE_CHOICES, verbose_name='Turi')
    quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Miqdor')
    balance_before = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Oldingi balans')
    balance_after = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Keyingi balans')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='movements', verbose_name='Foydalanuvchi'
    )
    warehouse_from = models.ForeignKey(
        'warehouses.Warehouse', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='movements_from',
        verbose_name='Qayerdan'
    )
    warehouse_to = models.ForeignKey(
        'warehouses.Warehouse', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='movements_to',
        verbose_name='Qayerga'
    )
    note = models.TextField(blank=True, verbose_name='Izoh')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Partiya harakati'
        verbose_name_plural = 'Partiya harakatlari'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.batch.batch_number} - {self.type} - {self.quantity}"
