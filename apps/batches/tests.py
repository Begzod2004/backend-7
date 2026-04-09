from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.products.models import Category, Unit, Product
from apps.warehouses.models import Warehouse
from apps.batches.models import Batch, BatchMovement

User = get_user_model()


class BatchModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Metall')
        self.unit = Unit.objects.create(name='Kilogramm', abbreviation='kg')
        self.product = Product.objects.create(name='Armatura', category=self.category, unit=self.unit, price=15000)
        self.warehouse = Warehouse.objects.create(name='Markaziy', capacity=10000)

    def test_auto_batch_number(self):
        batch = Batch.objects.create(
            product=self.product, warehouse=self.warehouse, unit=self.unit,
            quantity=100, min_quantity=10, price=15000,
        )
        self.assertTrue(batch.batch_number.startswith('BATCH-'))

    def test_total_value_calculated(self):
        batch = Batch.objects.create(
            product=self.product, warehouse=self.warehouse, unit=self.unit,
            quantity=100, price=15000,
        )
        self.assertEqual(batch.total_value, Decimal('100') * Decimal('15000'))

    def test_status_normal(self):
        batch = Batch.objects.create(
            product=self.product, warehouse=self.warehouse, unit=self.unit,
            quantity=100, min_quantity=10, price=15000,
        )
        self.assertEqual(batch.status, 'NORMAL')

    def test_status_low(self):
        batch = Batch.objects.create(
            product=self.product, warehouse=self.warehouse, unit=self.unit,
            quantity=5, min_quantity=10, price=15000,
        )
        self.assertEqual(batch.status, 'LOW')

    def test_status_empty(self):
        batch = Batch.objects.create(
            product=self.product, warehouse=self.warehouse, unit=self.unit,
            quantity=0, min_quantity=10, price=15000,
        )
        self.assertEqual(batch.status, 'EMPTY')

    def test_update_quantity_in(self):
        admin = User.objects.create_user(phone='+998900000400', password='Test!', first_name='A', last_name='B')
        batch = Batch.objects.create(
            product=self.product, warehouse=self.warehouse, unit=self.unit,
            quantity=100, min_quantity=10, price=15000,
        )
        batch.update_quantity(50, 'IN', admin)
        batch.refresh_from_db()
        self.assertEqual(batch.quantity, Decimal('150'))

    def test_update_quantity_out(self):
        admin = User.objects.create_user(phone='+998900000401', password='Test!', first_name='A', last_name='B')
        batch = Batch.objects.create(
            product=self.product, warehouse=self.warehouse, unit=self.unit,
            quantity=100, min_quantity=10, price=15000,
        )
        batch.update_quantity(30, 'OUT', admin)
        batch.refresh_from_db()
        self.assertEqual(batch.quantity, Decimal('70'))

    def test_movement_created_on_update(self):
        admin = User.objects.create_user(phone='+998900000402', password='Test!', first_name='A', last_name='B')
        batch = Batch.objects.create(
            product=self.product, warehouse=self.warehouse, unit=self.unit,
            quantity=100, min_quantity=10, price=15000,
        )
        batch.update_quantity(20, 'IN', admin)
        movements = BatchMovement.objects.filter(batch=batch)
        self.assertTrue(movements.exists())


class BatchAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            phone='+998900000410', password='Admin1234!',
            first_name='Admin', last_name='User', role='ADMIN',
        )
        self.category = Category.objects.create(name='Metall')
        self.unit = Unit.objects.create(name='Kilogramm', abbreviation='kg')
        self.product = Product.objects.create(name='Armatura', category=self.category, unit=self.unit, price=15000)
        self.warehouse = Warehouse.objects.create(name='Markaziy', capacity=10000)

    def test_create_batch(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.post('/api/batches/', {
            'product': self.product.id, 'warehouse': self.warehouse.id,
            'unit': self.unit.id, 'quantity': 100, 'min_quantity': 10, 'price': 15000,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(resp.data['batch_number'].startswith('BATCH-'))

    def test_list_batches(self):
        Batch.objects.create(
            product=self.product, warehouse=self.warehouse, unit=self.unit,
            quantity=100, price=15000,
        )
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/batches/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_filter_by_status(self):
        Batch.objects.create(
            product=self.product, warehouse=self.warehouse, unit=self.unit,
            quantity=0, min_quantity=10, price=15000,
        )
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/batches/?status=EMPTY')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_batch_movements_endpoint(self):
        batch = Batch.objects.create(
            product=self.product, warehouse=self.warehouse, unit=self.unit,
            quantity=100, price=15000,
        )
        self.client.force_authenticate(self.admin)
        resp = self.client.get(f'/api/batches/{batch.id}/movements/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


class BatchMovementAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            phone='+998900000420', password='Admin1234!',
            first_name='Admin', last_name='User', role='ADMIN',
        )
        category = Category.objects.create(name='Metall')
        unit = Unit.objects.create(name='Kilogramm', abbreviation='kg')
        product = Product.objects.create(name='Armatura', category=category, unit=unit, price=15000)
        warehouse = Warehouse.objects.create(name='Markaziy', capacity=10000)
        self.batch = Batch.objects.create(
            product=product, warehouse=warehouse, unit=unit,
            quantity=100, min_quantity=10, price=15000,
        )

    def test_create_movement_in(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.post('/api/movements/', {
            'batch': self.batch.id, 'type': 'IN', 'quantity': 50,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.batch.refresh_from_db()
        self.assertEqual(self.batch.quantity, Decimal('150'))

    def test_create_movement_out(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.post('/api/movements/', {
            'batch': self.batch.id, 'type': 'OUT', 'quantity': 30,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.batch.refresh_from_db()
        self.assertEqual(self.batch.quantity, Decimal('70'))

    def test_out_exceeds_quantity_fails(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.post('/api/movements/', {
            'batch': self.batch.id, 'type': 'OUT', 'quantity': 999,
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
