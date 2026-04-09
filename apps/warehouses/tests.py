from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.warehouses.models import Warehouse

User = get_user_model()


class WarehouseModelTest(TestCase):
    def test_create_warehouse(self):
        wh = Warehouse.objects.create(name='Markaziy', address='Toshkent', capacity=10000)
        self.assertEqual(str(wh), 'Markaziy')
        self.assertTrue(wh.is_active)

    def test_name_unique(self):
        Warehouse.objects.create(name='Ombor 1')
        with self.assertRaises(Exception):
            Warehouse.objects.create(name='Ombor 1')


class WarehouseAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            phone='+998900000300', password='Admin1234!',
            first_name='Admin', last_name='User', role='ADMIN',
        )
        self.warehouse = Warehouse.objects.create(name='Test Ombor', capacity=5000)
        self.kichik = User.objects.create_user(
            phone='+998900000301', password='User1234!',
            first_name='Kichik', last_name='Admin',
            role='KICHIK_OMBOR_ADMINI', warehouse=self.warehouse,
        )

    def test_admin_crud(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.post('/api/warehouses/', {'name': 'Yangi', 'capacity': 3000})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        wh_id = resp.data['id']
        resp = self.client.delete(f'/api/warehouses/{wh_id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_kichik_sees_only_own(self):
        Warehouse.objects.create(name='Boshqa', capacity=2000)
        self.client.force_authenticate(self.kichik)
        resp = self.client.get('/api/warehouses/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        results = resp.data.get('results', resp.data)
        for wh in results:
            self.assertEqual(wh['id'], self.warehouse.id)

    def test_kichik_cannot_delete(self):
        self.client.force_authenticate(self.kichik)
        resp = self.client.delete(f'/api/warehouses/{self.warehouse.id}/')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
