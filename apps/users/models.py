from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('Telefon raqam kiritilishi shart')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        return self.create_user(phone, password, **extra_fields)


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('KATTA_OMBOR_ADMINI', 'Katta ombor admini'),
        ('KICHIK_OMBOR_ADMINI', 'Kichik ombor admini'),
        ('HISOBCHI', 'Hisobchi'),
    )

    username = None
    phone = models.CharField(max_length=20, unique=True, verbose_name='Telefon')
    email = models.EmailField(unique=True, blank=True, null=True, verbose_name='Email')
    role = models.CharField(max_length=25, choices=ROLE_CHOICES, default='KICHIK_OMBOR_ADMINI', verbose_name='Rol')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Avatar')
    warehouse = models.ForeignKey(
        'warehouses.Warehouse', on_delete=models.SET_NULL,
        blank=True, null=True, related_name='assigned_users',
        verbose_name='Biriktirilgan ombor'
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone})"
