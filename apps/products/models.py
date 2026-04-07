from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Nomi')
    description = models.TextField(blank=True, verbose_name='Tavsif')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'
        ordering = ['name']

    def __str__(self):
        return self.name


class Unit(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Nomi')
    abbreviation = models.CharField(max_length=20, unique=True, verbose_name='Qisqartma')

    class Meta:
        verbose_name = "O'lchov birligi"
        verbose_name_plural = "O'lchov birliklari"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='Nomi')
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE,
        related_name='products', verbose_name='Kategoriya'
    )
    unit = models.ForeignKey(
        Unit, on_delete=models.PROTECT,
        related_name='products', verbose_name="O'lchov birligi"
    )
    min_quantity = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        verbose_name='Minimal miqdor'
    )
    price = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name='Narx'
    )
    image = models.ImageField(
        upload_to='products/', blank=True, null=True,
        verbose_name='Rasm'
    )
    description = models.TextField(blank=True, verbose_name='Tavsif')
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Mahsulot'
        verbose_name_plural = 'Mahsulotlar'
        ordering = ['name']

    def __str__(self):
        return self.name
