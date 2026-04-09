from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.products.models import Category, Unit, Product
from apps.warehouses.models import Warehouse
from apps.batches.models import Batch

User = get_user_model()


class ReportsAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            phone='+998900001300', password='Admin1234!',
            first_name='Admin', last_name='User', role='ADMIN',
        )
        category = Category.objects.create(name='Metall')
        unit = Unit.objects.create(name='Kg', abbreviation='kg')
        product = Product.objects.create(name='Armatura', category=category, unit=unit, price=15000)
        warehouse = Warehouse.objects.create(name='Markaziy', capacity=10000)
        Batch.objects.create(product=product, warehouse=warehouse, unit=unit, quantity=100, price=15000)
        Batch.objects.create(product=product, warehouse=warehouse, unit=unit, quantity=5, min_quantity=10, price=15000)

    def test_inventory_report(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/reports/inventory/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_movements_report(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/reports/movements/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_low_stock_report(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/reports/low-stock/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_warehouse_summary(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/reports/warehouse-summary/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_export_excel(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/reports/export/excel/?type=inventory')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_export_pdf(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/reports/export/pdf/?type=inventory')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_dashboard_stats(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/dashboard/stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_kichik_cannot_export(self):
        kichik = User.objects.create_user(
            phone='+998900001301', password='User1234!',
            first_name='K', last_name='A', role='KICHIK_OMBOR_ADMINI',
        )
        self.client.force_authenticate(kichik)
        resp = self.client.get('/api/reports/warehouse-summary/')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access(self):
        resp = self.client.get('/api/reports/inventory/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
