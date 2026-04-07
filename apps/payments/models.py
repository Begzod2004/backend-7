from django.db import models
from django.conf import settings


class Payment(models.Model):
    METHOD_CHOICES = (
        ('CASH', 'Naqd'),
        ('BANK_TRANSFER', "Bank o'tkazmasi"),
        ('OTHER', 'Boshqa'),
    )

    invoice = models.ForeignKey(
        'invoices.ShotInvoice', on_delete=models.CASCADE,
        related_name='payments', verbose_name='Faktura'
    )
    supplier = models.ForeignKey(
        'suppliers.Supplier', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='payments',
        verbose_name='Yetkazib beruvchi'
    )
    amount = models.DecimalField(
        max_digits=18, decimal_places=2,
        verbose_name="To'langan summa"
    )
    payment_date = models.DateField(verbose_name="To'lov sanasi")
    payment_method = models.CharField(
        max_length=20, choices=METHOD_CHOICES,
        default='CASH', verbose_name="To'lov usuli"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, verbose_name='Yaratuvchi'
    )
    note = models.TextField(blank=True, verbose_name='Izoh')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "To'lov"
        verbose_name_plural = "To'lovlar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.invoice.invoice_number} — {self.amount}"
