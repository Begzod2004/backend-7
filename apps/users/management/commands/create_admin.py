from django.core.management.base import BaseCommand
from apps.users.models import CustomUser


class Command(BaseCommand):
    help = 'Admin foydalanuvchi yaratish'

    def handle(self, *args, **options):
        phone = '+998901234567'
        email = 'admin@matrix.uz'
        password = 'Admin1234!'

        if CustomUser.objects.filter(phone=phone).exists():
            self.stdout.write(self.style.WARNING(f'Admin already exists: {phone}'))
            return

        user = CustomUser.objects.create_superuser(
            phone=phone,
            password=password,
            email=email,
            first_name='Admin',
            last_name='7Trest',
        )
        self.stdout.write(self.style.SUCCESS(
            f'Admin yaratildi!\n'
            f'  Phone: {phone}\n'
            f'  Email: {email}\n'
            f'  Password: {password}'
        ))
