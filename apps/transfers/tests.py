from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.products.models import Category, Unit, Product
from apps.warehouses.models import Warehouse
from apps.batches.models import Batch
from apps.transfers.models import Transfer, TransferItem

User = get_user_model()


class TransferModelTest(TestCase):
    def setUp(self):
        self.wh1 = Warehouse.objects.create(name='Ombor 1', capacity=5000)
        self.wh2 = Warehouse.objects.create(name='Ombor 2', capacity=3000)
        self.admin = User.objects.create_user(
            phone='+998900000800', password='Test!', first_name='A', last_name='B', role='ADMIN',
        )

    def test_auto_transfer_number(self):
        t = Transfer.objects.create(
            from_warehouse=self.wh1, to_warehouse=self.wh2, created_by=self.admin,
        )
        self.assertTrue(t.transfer_number.startswith('TRF-'))

    def test_default_status(self):
        t = Transfer.objects.create(
            from_warehouse=self.wh1, to_warehouse=self.wh2, created_by=self.admin,
        )
        self.assertEqual(t.status, 'PENDING')


class TransferAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            phone='+998900000810', password='Admin1234!',
            first_name='Admin', last_name='User', role='ADMIN',
        )
        self.wh1 = Warehouse.objects.create(name='Ombor 1', capacity=5000)
        self.wh2 = Warehouse.objects.create(name='Ombor 2', capacity=3000)
        category = Category.objects.create(name='Metall')
        self.unit = Unit.objects.create(name='Kg', abbreviation='kg')
        self.product = Product.objects.create(name='Armatura', category=category, unit=self.unit, price=15000)
        self.batch = Batch.objects.create(
            product=self.product, warehouse=self.wh1, unit=self.unit,
            quantity=100, min_quantity=10, price=15000,
        )

    def test_create_transfer(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.post('/api/transfers/', {
            'from_warehouse': self.wh1.id,
            'to_warehouse': self.wh2.id,
            'driver_name': 'Alisher',
            'vehicle_number': '01A123BB',
            'items': [
                {'batch': self.batch.id, 'product': self.product.id, 'quantity': 20},
            ],
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_list_transfers(self):
        Transfer.objects.create(
            from_warehouse=self.wh1, to_warehouse=self.wh2, created_by=self.admin,
        )
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/transfers/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_same_warehouse_rejected(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.post('/api/transfers/', {
            'from_warehouse': self.wh1.id,
            'to_warehouse': self.wh1.id,
            'items': [
                {'batch': self.batch.id, 'product': self.product.id, 'quantity': 10},
            ],
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_deliver_transfer(self):
        transfer = Transfer.objects.create(
            from_warehouse=self.wh1, to_warehouse=self.wh2, created_by=self.admin,
        )
        TransferItem.objects.create(
            transfer=transfer, batch=self.batch, product=self.product, quantity=20,
        )
        self.client.force_authenticate(self.admin)
        resp = self.client.put(f'/api/transfers/{transfer.id}/deliver/', {
            'items': [{'id': transfer.items.first().id, 'received_quantity': 20}],
        }, format='json')
        self.assertIn(resp.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
