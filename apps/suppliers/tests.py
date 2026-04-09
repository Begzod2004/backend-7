from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.suppliers.models import Supplier

User = get_user_model()


class SupplierModelTest(TestCase):
    def test_create_supplier(self):
        s = Supplier.objects.create(name='Toshkent Metall', inn='123456789', phone='+998712345678')
        self.assertEqual(str(s), 'Toshkent Metall')
        self.assertEqual(s.rating, 5)
        self.assertTrue(s.is_active)

    def test_inn_unique(self):
        Supplier.objects.create(name='S1', inn='111111111')
        with self.assertRaises(Exception):
            Supplier.objects.create(name='S2', inn='111111111')


class SupplierAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            phone='+998900000700', password='Admin1234!',
            first_name='Admin', last_name='User', role='ADMIN',
        )

    def test_create_supplier(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.post('/api/suppliers/', {
            'name': 'Test Supplier', 'inn': '999888777',
            'phone': '+998712345678', 'rating': 4,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_list_suppliers(self):
        Supplier.objects.create(name='S1')
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/suppliers/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_supplier_stats(self):
        s = Supplier.objects.create(name='Test')
        self.client.force_authenticate(self.admin)
        resp = self.client.get(f'/api/suppliers/{s.id}/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_filter_by_rating(self):
        Supplier.objects.create(name='Good', rating=5)
        Supplier.objects.create(name='Mid', rating=3)
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/suppliers/?rating=5')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_search_supplier(self):
        Supplier.objects.create(name='Navoiy Sement')
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/suppliers/?search=Navoiy')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
