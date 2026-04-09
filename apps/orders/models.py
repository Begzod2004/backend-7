from django.db import models
from django.conf import settings
from core.utils import generate_number


class Order(models.Model):
    TYPE_CHOICES = (
        ('INCOMING', 'Kirim'),
        ('OUTGOING', 'Chiqim'),
    )
    STATUS_CHOICES = (
        ('NEW', 'Yangi'),
        ('PROCESSING', 'Jarayonda'),
        ('COMPLETED', 'Bajarildi'),
        ('CANCELLED', 'Bekor qilindi'),
        ('ON_HOLD', 'Kutilmoqda'),
        ('DOCUMENT_ERROR', 'Hujjatda xatolik'),
        ('RESUBMITTED', 'Qayta yuborildi'),
        ('ACCEPTED', 'Qabul qilindi'),
    )

    order_number = models.CharField(max_length=20, unique=True, editable=False, verbose_name='Buyurtma raqami')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='OUTGOING', verbose_name='Turi')
    warehouse = models.ForeignKey(
        'warehouses.Warehouse', on_delete=models.CASCADE,
        related_name='orders', verbose_name='Ombor'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='orders', verbose_name='Yaratuvchi'
    )
    customer_name = models.CharField(max_length=255, blank=True, verbose_name='Mijoz nomi')
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='Umumiy summa')
    note = models.TextField(blank=True, verbose_name='Izoh')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='NEW', verbose_name='Holat')
    order_date = models.DateField(auto_now_add=True, verbose_name='Buyurtma sanasi')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Buyurtma'
        verbose_name_plural = 'Buyurtmalar'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_number} - {self.get_type_display()}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = generate_number('ORD', Order, 'order_number')
        super().save(*args, **kwargs)

    def calculate_total(self):
        self.total_amount = sum(
            item.total or 0 for item in self.items.all()
        )
        self.save(update_fields=['total_amount'])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Buyurtma')
    category = models.ForeignKey(
        'products.Category', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='order_items',
        verbose_name='Kategoriya'
    )
    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE,
        related_name='order_items', verbose_name='Mahsulot'
    )
    batch = models.ForeignKey(
        'batches.Batch', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='order_items',
        verbose_name='Partiya'
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='So\'ralgan miqdor')
    fulfilled_quantity = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        verbose_name='Bajarilgan miqdor'
    )
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='Narx')
    total = models.DecimalField(max_digits=18, decimal_places=2, default=0, editable=False, verbose_name='Jami')
    barcode_scanned = models.CharField(max_length=50, blank=True, verbose_name='Skanerlangan barcode')

    class Meta:
        verbose_name = 'Buyurtma elementi'
        verbose_name_plural = 'Buyurtma elementlari'

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        self.total = self.fulfilled_quantity * self.price
        super().save(*args, **kwargs)


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history', verbose_name='Buyurtma')
    status = models.CharField(max_length=15, choices=Order.STATUS_CHOICES, verbose_name='Holat')
    note = models.TextField(blank=True, verbose_name='Izoh')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Buyurtma holat tarixi'
        verbose_name_plural = 'Buyurtma holat tarixlari'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order.order_number} → {self.status}"


class Return(models.Model):
    """Vozvrat — kichik ombor katta omborga mahsulot qaytaradi."""
    STATUS_CHOICES = (
        ('NEW', 'Yangi'),
        ('ACCEPTED', 'Qabul qilindi'),
        ('REJECTED', 'Rad etildi'),
        ('RESUBMITTED', 'Qayta yuborildi'),
    )

    return_number = models.CharField(max_length=20, unique=True, editable=False, verbose_name='Vozvrat raqami')
    warehouse = models.ForeignKey(
        'warehouses.Warehouse', on_delete=models.CASCADE,
        related_name='returns', verbose_name='Kichik ombor'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='returns', verbose_name='Yaratuvchi'
    )
    reason = models.TextField(verbose_name='Qaytarish sababi')
    note = models.TextField(blank=True, verbose_name='Izoh')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='NEW', verbose_name='Holat')
    reject_note = models.TextField(blank=True, verbose_name='Rad etish sababi')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Vozvrat'
        verbose_name_plural = 'Vozvratlar'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.return_number:
            self.return_number = generate_number('RET', Return, 'return_number')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.return_number


class ReturnItem(models.Model):
    ret = models.ForeignKey(Return, on_delete=models.CASCADE, related_name='items', verbose_name='Vozvrat')
    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE,
        related_name='return_items', verbose_name='Mahsulot'
    )
    batch = models.ForeignKey(
        'batches.Batch', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='return_items',
        verbose_name='Partiya'
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Miqdor')
    note = models.TextField(blank=True, verbose_name='Izoh')

    class Meta:
        verbose_name = 'Vozvrat elementi'
        verbose_name_plural = 'Vozvrat elementlari'

    def __str__(self):
        return f"{self.ret.return_number} — {self.product.name}"
