from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.warehouses.models import Warehouse

User = get_user_model()


class CustomUserManagerTest(TestCase):
    def test_create_user_with_phone(self):
        user = User.objects.create_user(
            phone='+998900000001', password='Test1234!',
            first_name='Test', last_name='User',
        )
        self.assertEqual(user.phone, '+998900000001')
        self.assertTrue(user.check_password('Test1234!'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_without_phone_raises(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(phone='', password='Test1234!')

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            phone='+998900000002', password='Admin1234!',
            first_name='Admin', last_name='User',
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.role, 'ADMIN')


class CustomUserModelTest(TestCase):
    def test_str_representation(self):
        user = User.objects.create_user(
            phone='+998900000003', password='Test1234!',
            first_name='Ali', last_name='Valiyev',
        )
        self.assertIn('Ali', str(user))

    def test_default_role(self):
        user = User.objects.create_user(
            phone='+998900000004', password='Test1234!',
            first_name='Test', last_name='User',
        )
        self.assertEqual(user.role, 'KICHIK_OMBOR_ADMINI')

    def test_phone_unique(self):
        User.objects.create_user(phone='+998900000005', password='Test1234!', first_name='A', last_name='B')
        with self.assertRaises(Exception):
            User.objects.create_user(phone='+998900000005', password='Test1234!', first_name='C', last_name='D')

    def test_warehouse_assignment(self):
        warehouse = Warehouse.objects.create(name='Test Ombor', capacity=1000)
        user = User.objects.create_user(
            phone='+998900000006', password='Test1234!',
            first_name='Test', last_name='User', warehouse=warehouse,
        )
        self.assertEqual(user.warehouse, warehouse)


class UserAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            phone='+998900000010', password='Admin1234!',
            first_name='Admin', last_name='User', role='ADMIN',
        )
        self.kichik = User.objects.create_user(
            phone='+998900000012', password='User1234!',
            first_name='Kichik', last_name='Admin', role='KICHIK_OMBOR_ADMINI',
        )

    def test_admin_can_list_users(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/users/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_admin_can_create_user(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.post('/api/users/', {
            'phone': '+998900000020', 'password': 'Test1234!',
            'first_name': 'Yangi', 'last_name': 'User', 'role': 'HISOBCHI',
        })
        self.assertIn(resp.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])

    def test_unauthenticated_cannot_access(self):
        resp = self.client.get('/api/users/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
