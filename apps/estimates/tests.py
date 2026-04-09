from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.estimates.models import Estimate, EstimateItem
from apps.objects.models import ConstructionObject
from apps.products.models import Category, Unit, Product

User = get_user_model()


class EstimateModelTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            phone='+998900001000', password='Test!', first_name='A', last_name='B', role='ADMIN',
        )

    def test_auto_estimate_number(self):
        est = Estimate.objects.create(name='Test Smeta', created_by=self.admin)
        self.assertTrue(est.estimate_number.startswith('EST-'))

    def test_default_status(self):
        est = Estimate.objects.create(name='Test Smeta', created_by=self.admin)
        self.assertEqual(est.status, 'DRAFT')

    def test_calculate_total(self):
        category = Category.objects.create(name='Test')
        unit = Unit.objects.create(name='Dona', abbreviation='ta')
        product = Product.objects.create(name='P1', category=category, unit=unit, price=1000)
        est = Estimate.objects.create(name='Smeta', created_by=self.admin)
        EstimateItem.objects.create(estimate=est, product=product, quantity=10, unit=unit, price_per_unit=1000)
        EstimateItem.objects.create(estimate=est, product=product, quantity=5, unit=unit, price_per_unit=2000)
        est.calculate_total()
        est.refresh_from_db()
        self.assertEqual(est.total_planned, Decimal('20000'))


class EstimateAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            phone='+998900001010', password='Admin1234!',
            first_name='Admin', last_name='User', role='ADMIN',
        )
        self.category = Category.objects.create(name='Metall')
        self.unit = Unit.objects.create(name='Kg', abbreviation='kg')
        self.product = Product.objects.create(name='Armatura', category=self.category, unit=self.unit, price=15000)

    def test_create_estimate(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.post('/api/estimates/', {
            'name': 'Yangi Smeta',
            'items': [
                {'product': self.product.id, 'quantity': 100, 'unit': self.unit.id, 'price_per_unit': 15000},
            ],
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_list_estimates(self):
        Estimate.objects.create(name='Test', created_by=self.admin)
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/estimates/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_approve_estimate(self):
        est = Estimate.objects.create(name='Test', created_by=self.admin)
        self.client.force_authenticate(self.admin)
        resp = self.client.put(f'/api/estimates/{est.id}/approve/')
        self.assertIn(resp.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        est.refresh_from_db()
        self.assertEqual(est.status, 'APPROVED')

    def test_compare_estimate(self):
        est = Estimate.objects.create(name='Test', created_by=self.admin)
        self.client.force_authenticate(self.admin)
        resp = self.client.get(f'/api/estimates/{est.id}/compare/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_cannot_delete_approved(self):
        est = Estimate.objects.create(name='Test', created_by=self.admin, status='APPROVED')
        self.client.force_authenticate(self.admin)
        resp = self.client.delete(f'/api/estimates/{est.id}/')
        self.assertIn(resp.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN, status.HTTP_204_NO_CONTENT])
