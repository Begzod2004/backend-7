from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.objects.models import ConstructionObject, ObjectMaterial, ObjectExpense
from apps.products.models import Category, Unit, Product
from apps.warehouses.models import Warehouse
from apps.batches.models import Batch

User = get_user_model()


class ConstructionObjectModelTest(TestCase):
    def test_create_object(self):
        obj = ConstructionObject.objects.create(
            name='Chilanzar 9-uy', address='Toshkent', budget=500000000,
        )
        self.assertEqual(str(obj), 'Chilanzar 9-uy')
        self.assertEqual(obj.status, 'PLANNING')


class ConstructionObjectAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            phone='+998900000900', password='Admin1234!',
            first_name='Admin', last_name='User', role='ADMIN',
        )
        self.category = Category.objects.create(name='Metall')
        self.unit = Unit.objects.create(name='Kg', abbreviation='kg')
        self.product = Product.objects.create(name='Armatura', category=self.category, unit=self.unit, price=15000)
        self.warehouse = Warehouse.objects.create(name='Markaziy', capacity=10000)

    def test_create_object(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.post('/api/objects/', {
            'name': 'Yangi Obyekt', 'address': 'Toshkent', 'budget': 100000000,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_list_objects(self):
        ConstructionObject.objects.create(name='Test', budget=100)
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/objects/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_add_material(self):
        obj = ConstructionObject.objects.create(name='Test Mat', budget=100000000)
        self.client.force_authenticate(self.admin)
        resp = self.client.post(f'/api/objects/{obj.id}/materials/', {
            'object': obj.id,
            'product': self.product.id,
            'planned_quantity': 1000,
            'used_quantity': 0,
            'unit': self.unit.id,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_add_expense(self):
        obj = ConstructionObject.objects.create(name='Test Exp', budget=100000000)
        batch = Batch.objects.create(
            product=self.product, warehouse=self.warehouse, unit=self.unit,
            quantity=100, price=15000,
        )
        self.client.force_authenticate(self.admin)
        resp = self.client.post(f'/api/objects/{obj.id}/expenses/', {
            'object': obj.id,
            'batch': batch.id,
            'quantity': 10,
            'price_per_unit': 15000,
            'warehouse': self.warehouse.id,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_summary(self):
        obj = ConstructionObject.objects.create(name='Test', budget=100000000)
        self.client.force_authenticate(self.admin)
        resp = self.client.get(f'/api/objects/{obj.id}/summary/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_kichik_cannot_create(self):
        kichik = User.objects.create_user(
            phone='+998900000901', password='User1234!',
            first_name='K', last_name='A', role='KICHIK_OMBOR_ADMINI',
        )
        self.client.force_authenticate(kichik)
        resp = self.client.post('/api/objects/', {'name': 'X', 'budget': 100})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
