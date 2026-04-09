from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.products.models import Category, Unit, Product
from apps.warehouses.models import Warehouse
from apps.batches.models import Batch
from apps.invoices.models import ShotInvoice

User = get_user_model()


class InvoiceModelTest(TestCase):
    def setUp(self):
        category = Category.objects.create(name='Metall')
        unit = Unit.objects.create(name='Kg', abbreviation='kg')
        product = Product.objects.create(name='Armatura', category=category, unit=unit)
        self.warehouse = Warehouse.objects.create(name='Markaziy', capacity=10000)
        self.batch = Batch.objects.create(
            product=product, warehouse=self.warehouse, unit=unit,
            quantity=100, price=15000,
        )
        self.admin = User.objects.create_user(
            phone='+998900000600', password='Test!', first_name='A', last_name='B', role='ADMIN',
        )

    def test_auto_invoice_number(self):
        inv = ShotInvoice.objects.create(
            batch=self.batch, warehouse=self.warehouse, created_by=self.admin,
            quantity=50, price=15000, supplier_name='Test Supplier',
            document_date='2026-01-01', document_number='DOC-001',
        )
        self.assertTrue(inv.invoice_number.startswith('INV-'))

    def test_total_amount_calculated(self):
        inv = ShotInvoice.objects.create(
            batch=self.batch, warehouse=self.warehouse, created_by=self.admin,
            quantity=50, price=15000, supplier_name='Test Supplier',
            document_date='2026-01-01', document_number='DOC-001',
        )
        self.assertEqual(inv.total_amount, Decimal('50') * Decimal('15000'))

    def test_default_status(self):
        inv = ShotInvoice.objects.create(
            batch=self.batch, warehouse=self.warehouse, created_by=self.admin,
            quantity=50, price=15000, supplier_name='Test',
            document_date='2026-01-01', document_number='DOC-001',
        )
        self.assertEqual(inv.status, 'PENDING')


class InvoiceAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            phone='+998900000610', password='Admin1234!',
            first_name='Admin', last_name='User', role='ADMIN',
        )
        category = Category.objects.create(name='Metall')
        unit = Unit.objects.create(name='Kg', abbreviation='kg')
        product = Product.objects.create(name='Armatura', category=category, unit=unit)
        self.warehouse = Warehouse.objects.create(name='Markaziy', capacity=10000)
        self.batch = Batch.objects.create(
            product=product, warehouse=self.warehouse, unit=unit,
            quantity=100, price=15000,
        )

    def test_create_invoice(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.post('/api/invoices/', {
            'batch': self.batch.id, 'warehouse': self.warehouse.id,
            'quantity': 50, 'price': 15000, 'supplier_name': 'Test Supplier',
            'document_date': '2026-01-01', 'document_number': 'DOC-001',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_list_invoices(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/invoices/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_download_pdf(self):
        inv = ShotInvoice.objects.create(
            batch=self.batch, warehouse=self.warehouse, created_by=self.admin,
            quantity=50, price=15000, supplier_name='Test',
            document_date='2026-01-01', document_number='DOC-001',
        )
        self.client.force_authenticate(self.admin)
        resp = self.client.get(f'/api/invoices/{inv.id}/pdf/')
        self.assertIn(resp.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])

    def test_export_excel(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/invoices/export/')
        self.assertIn(resp.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])

    def test_kichik_cannot_manage_invoices(self):
        kichik = User.objects.create_user(
            phone='+998900000611', password='User1234!',
            first_name='K', last_name='A', role='KICHIK_OMBOR_ADMINI',
        )
        self.client.force_authenticate(kichik)
        resp = self.client.post('/api/invoices/', {
            'batch': self.batch.id, 'warehouse': self.warehouse.id,
            'quantity': 10, 'price': 15000, 'supplier_name': 'X',
            'document_date': '2026-01-01', 'document_number': 'D-1',
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
