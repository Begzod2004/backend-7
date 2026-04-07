from django.db import models


class Supplier(models.Model):
    name = models.CharField(max_length=255, verbose_name='Kompaniya nomi')
    inn = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name='INN/STIR')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefon')
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    address = models.TextField(blank=True, verbose_name='Manzil')
    contact_person = models.CharField(max_length=255, blank=True, verbose_name='Aloqa shaxsi')
    rating = models.PositiveSmallIntegerField(default=5, verbose_name='Reyting')
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    note = models.TextField(blank=True, verbose_name='Izoh')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Yetkazib beruvchi'
        verbose_name_plural = 'Yetkazib beruvchilar'
        ordering = ['name']

    def __str__(self):
        return self.name
