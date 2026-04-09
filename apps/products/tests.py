from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.products.models import Category, Unit, Product

User = get_user_model()


class CategoryModelTest(TestCase):
    def test_create_category(self):
        cat = Category.objects.create(name='Metall', description='Metall buyumlar')
        self.assertEqual(str(cat), 'Metall')

    def test_name_unique(self):
        Category.objects.create(name='Qurilish')
        with self.assertRaises(Exception):
            Category.objects.create(name='Qurilish')


class UnitModelTest(TestCase):
    def test_create_unit(self):
        unit = Unit.objects.create(name='Kilogramm', abbreviation='kg')
        self.assertIn('kg', str(unit))

    def test_abbreviation_unique(self):
        Unit.objects.create(name='Kilogramm', abbreviation='kg')
        with self.assertRaises(Exception):
            Unit.objects.create(name='Kilogramm2', abbreviation='kg')


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Cat')
        self.unit = Unit.objects.create(name='Dona', abbreviation='ta')

    def test_create_product(self):
        p = Product.objects.create(name='Armatura 12mm', category=self.category, unit=self.unit, price=15000)
        self.assertEqual(p.name, 'Armatura 12mm')
        self.assertTrue(p.is_active)

    def test_product_defaults(self):
        p = Product.objects.create(name='Test', category=self.category, unit=self.unit)
        self.assertEqual(p.price, 0)
        self.assertEqual(p.min_quantity, 0)


class CategoryAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            phone='+998900000200', password='Admin1234!',
            first_name='Admin', last_name='User', role='ADMIN',
        )
        self.hisobchi = User.objects.create_user(
            phone='+998900000201', password='User1234!',
            first_name='Hisobchi', last_name='User', role='HISOBCHI',
        )

    def test_admin_crud(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.post('/api/categories/', {'name': 'Yangi'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        cat_id = resp.data['id']
        resp = self.client.put(f'/api/categories/{cat_id}/', {'name': 'Yangilangan'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.client.delete(f'/api/categories/{cat_id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_hisobchi_read_only(self):
        Category.objects.create(name='Test')
        self.client.force_authenticate(self.hisobchi)
        resp = self.client.get('/api/categories/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.client.post('/api/categories/', {'name': 'Taqiqlangan'})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class ProductAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            phone='+998900000220', password='Admin1234!',
            first_name='Admin', last_name='User', role='ADMIN',
        )
        self.category = Category.objects.create(name='Metall')
        self.unit = Unit.objects.create(name='Kilogramm', abbreviation='kg')

    def test_create_product(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.post('/api/products/', {
            'name': 'Armatura 12mm', 'category': self.category.id,
            'unit': self.unit.id, 'price': 15000,
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_filter_by_category(self):
        Product.objects.create(name='P1', category=self.category, unit=self.unit)
        self.client.force_authenticate(self.admin)
        resp = self.client.get(f'/api/products/?category={self.category.id}')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_search_product(self):
        Product.objects.create(name='Sement M400', category=self.category, unit=self.unit)
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/products/?search=Sement')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
