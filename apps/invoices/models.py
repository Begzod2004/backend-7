from django.db import models
from django.conf import settings


class ShotInvoice(models.Model):
    """Shot-faktura — partiya yaratilganda avtomatik yaratiladi."""

    invoice_number = models.CharField(
        max_length=100, verbose_name='Shot-faktura raqami'
    )
    batch = models.OneToOneField(
        'batches.Batch', on_delete=models.CASCADE,
        related_name='invoice', verbose_name='Partiya'
    )
    warehouse = models.ForeignKey(
        'warehouses.Warehouse', on_delete=models.CASCADE,
        related_name='invoices', verbose_name='Ombor'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='invoices', verbose_name='Yaratuvchi'
    )
    file = models.FileField(
        upload_to='invoices/', blank=True, null=True,
        verbose_name='Hujjat fayli'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Shot faktura'
        verbose_name_plural = 'Shot fakturalar'
        ordering = ['-created_at']

    def __str__(self):
        return self.invoice_number

    @property
    def stock_status(self):
        """Omborda mavjud / mavjud emas — partiya miqdoriga qarab."""
        if self.batch.quantity > 0:
            return 'AVAILABLE'
        return 'UNAVAILABLE'

    @property
    def confirmation_status(self):
        """Tasdiqlangan / tasdiqlanmagan — file borligiga qarab."""
        if self.file:
            return 'CONFIRMED'
        return 'UNCONFIRMED'
