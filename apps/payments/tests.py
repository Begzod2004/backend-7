from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.products.models import Category, Unit, Product
from apps.warehouses.models import Warehouse
from apps.batches.models import Batch
from apps.invoices.models import ShotInvoice
from apps.suppliers.models import Supplier
from apps.payments.models import Payment

User = get_user_model()


class PaymentModelTest(TestCase):
    def setUp(self):
        category = Category.objects.create(name='Metall')
        unit = Unit.objects.create(name='Kg', abbreviation='kg')
        product = Product.objects.create(name='Armatura', category=category, unit=unit)
        warehouse = Warehouse.objects.create(name='Markaziy', capacity=10000)
        batch = Batch.objects.create(product=product, warehouse=warehouse, unit=unit, quantity=100, price=15000)
        self.admin = User.objects.create_user(
            phone='+998900001100', password='Test!', first_name='A', last_name='B', role='ADMIN',
        )
        self.invoice = ShotInvoice.objects.create(
            batch=batch, warehouse=warehouse, created_by=self.admin,
            quantity=50, price=15000, supplier_name='Test',
            document_date='2026-01-01', document_number='DOC-1',
        )

    def test_create_payment(self):
        p = Payment.objects.create(
            invoice=self.invoice, amount=100000,
            payment_date='2026-01-15', payment_method='CASH',
            created_by=self.admin,
        )
        self.assertEqual(p.amount, 100000)
        self.assertEqual(p.payment_method, 'CASH')


class PaymentAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            phone='+998900001110', password='Admin1234!',
            first_name='Admin', last_name='User', role='ADMIN',
        )
        category = Category.objects.create(name='Metall')
        unit = Unit.objects.create(name='Kg', abbreviation='kg')
        product = Product.objects.create(name='Armatura', category=category, unit=unit)
        warehouse = Warehouse.objects.create(name='Markaziy', capacity=10000)
        batch = Batch.objects.create(product=product, warehouse=warehouse, unit=unit, quantity=100, price=15000)
        self.invoice = ShotInvoice.objects.create(
            batch=batch, warehouse=warehouse, created_by=self.admin,
            quantity=50, price=15000, supplier_name='Test',
            document_date='2026-01-01', document_number='DOC-1',
        )

    def test_create_payment(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.post('/api/payments/', {
            'invoice': self.invoice.id, 'amount': 100000,
            'payment_date': '2026-01-15', 'payment_method': 'CASH',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_list_payments(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/payments/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_debt_summary(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/payments/debt-summary/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
