from django.db import models
from django.conf import settings


class ConstructionObject(models.Model):
    STATUS_CHOICES = (
        ('PLANNING', 'Rejalashtirilmoqda'),
        ('ACTIVE', 'Faol'),
        ('COMPLETED', 'Tugallangan'),
        ('SUSPENDED', "To'xtatilgan"),
    )
    name = models.CharField(max_length=255, verbose_name='Nomi')
    address = models.TextField(blank=True, verbose_name='Manzil')
    start_date = models.DateField(null=True, blank=True, verbose_name='Boshlanish sanasi')
    end_date = models.DateField(null=True, blank=True, verbose_name='Tugash sanasi')
    responsible_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='construction_objects',
        verbose_name="Mas'ul shaxs"
    )
    budget = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='Byudjet')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PLANNING', verbose_name='Holat')
    description = models.TextField(blank=True, verbose_name='Tavsif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Qurilish ob'ekti"
        verbose_name_plural = "Qurilish ob'ektlari"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ObjectMaterial(models.Model):
    object = models.ForeignKey(
        ConstructionObject, on_delete=models.CASCADE,
        related_name='materials', verbose_name="Ob'ekt"
    )
    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE,
        related_name='object_materials', verbose_name='Mahsulot'
    )
    planned_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Rejalashtirilgan miqdor')
    used_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Sarflangan miqdor')
    unit = models.ForeignKey(
        'products.Unit', on_delete=models.PROTECT,
        verbose_name="O'lchov birligi"
    )
    note = models.TextField(blank=True, verbose_name='Izoh')

    class Meta:
        verbose_name = "Ob'ekt materiali"
        verbose_name_plural = "Ob'ekt materiallari"

    def __str__(self):
        return f"{self.object.name} — {self.product.name}"


class ObjectExpense(models.Model):
    object = models.ForeignKey(
        ConstructionObject, on_delete=models.CASCADE,
        related_name='expenses', verbose_name="Ob'ekt"
    )
    batch = models.ForeignKey(
        'batches.Batch', on_delete=models.CASCADE,
        related_name='object_expenses', verbose_name='Partiya'
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Miqdor')
    price_per_unit = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Birlik narxi')
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, editable=False, verbose_name='Jami summa')
    taken_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, verbose_name='Kim oldi'
    )
    warehouse = models.ForeignKey(
        'warehouses.Warehouse', on_delete=models.CASCADE,
        verbose_name='Ombor'
    )
    note = models.TextField(blank=True, verbose_name='Izoh')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ob'ekt xarajati"
        verbose_name_plural = "Ob'ekt xarajatlari"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        self.total_amount = self.quantity * self.price_per_unit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.object.name} — {self.batch.batch_number}"
