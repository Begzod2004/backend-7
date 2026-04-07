from django.db import models
from django.conf import settings
from core.utils import generate_number


class ShotInvoice(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Kutilmoqda'),
        ('PAID', "To'langan"),
        ('CANCELLED', 'Bekor qilingan'),
    )

    invoice_number = models.CharField(max_length=20, unique=True, editable=False, verbose_name='Faktura raqami')
    batch = models.ForeignKey(
        'batches.Batch', on_delete=models.CASCADE,
        related_name='invoices', verbose_name='Partiya'
    )
    warehouse = models.ForeignKey(
        'warehouses.Warehouse', on_delete=models.CASCADE,
        related_name='invoices', verbose_name='Ombor'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='invoices', verbose_name='Yaratuvchi'
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Miqdor')
    price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Narx')
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, editable=False, verbose_name='Umumiy summa')
    supplier = models.ForeignKey(
        'suppliers.Supplier', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='invoices',
        verbose_name='Yetkazib beruvchi (tanlash)'
    )
    supplier_name = models.CharField(max_length=255, verbose_name='Yetkazib beruvchi')
    document_date = models.DateField(verbose_name='Hujjat sanasi')
    document_number = models.CharField(max_length=100, verbose_name='Hujjat raqami')
    note = models.TextField(blank=True, verbose_name='Izoh')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING', verbose_name='Holat')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Shot faktura'
        verbose_name_plural = 'Shot fakturalar'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.invoice_number} - {self.supplier_name}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = generate_number('INV', ShotInvoice, 'invoice_number')
        self.total_amount = self.quantity * self.price
        super().save(*args, **kwargs)
