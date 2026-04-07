from django.db import models
from django.conf import settings
from core.utils import generate_number


class Estimate(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Qoralama'),
        ('APPROVED', 'Tasdiqlangan'),
        ('REJECTED', 'Rad etilgan'),
    )

    estimate_number = models.CharField(
        max_length=20, unique=True, editable=False,
        verbose_name='Smeta raqami'
    )
    object = models.ForeignKey(
        'objects.ConstructionObject', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='estimates',
        verbose_name="Ob'ekt"
    )
    name = models.CharField(max_length=255, verbose_name='Smeta nomi')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='created_estimates',
        verbose_name='Yaratuvchi'
    )
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES,
        default='DRAFT', verbose_name='Holat'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_estimates',
        verbose_name='Tasdiqlagan'
    )
    total_planned = models.DecimalField(
        max_digits=18, decimal_places=2, default=0,
        editable=False, verbose_name='Jami rejalashtirilgan'
    )
    note = models.TextField(blank=True, verbose_name='Izoh')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Smeta'
        verbose_name_plural = 'Smetalar'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.estimate_number:
            self.estimate_number = generate_number('EST', Estimate, 'estimate_number')
        super().save(*args, **kwargs)

    def calculate_total(self):
        total = sum(item.total for item in self.items.all())
        self.total_planned = total
        self.save(update_fields=['total_planned'])

    def __str__(self):
        return f"{self.estimate_number} — {self.name}"


class EstimateItem(models.Model):
    estimate = models.ForeignKey(
        Estimate, on_delete=models.CASCADE,
        related_name='items', verbose_name='Smeta'
    )
    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE,
        verbose_name='Mahsulot'
    )
    quantity = models.DecimalField(
        max_digits=12, decimal_places=2,
        verbose_name='Miqdor'
    )
    unit = models.ForeignKey(
        'products.Unit', on_delete=models.PROTECT,
        verbose_name="O'lchov birligi"
    )
    price_per_unit = models.DecimalField(
        max_digits=15, decimal_places=2,
        verbose_name='Birlik narxi'
    )
    total = models.DecimalField(
        max_digits=18, decimal_places=2, editable=False,
        verbose_name='Jami'
    )
    note = models.TextField(blank=True, verbose_name='Izoh')

    class Meta:
        verbose_name = 'Smeta qatori'
        verbose_name_plural = 'Smeta qatorlari'

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.price_per_unit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.estimate.estimate_number} — {self.product.name}"
