from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from core.permissions import (
    IsAdmin, IsKattaOmborAdmin, IsKichikOmborAdmin, IsHisobchi,
    IsAdminOrKattaOmborAdmin, IsAdminOrKattaOrKichik, IsAdminOrKattaOrHisobchi,
    CanManageInvoices,
)
from core.utils import generate_number
from apps.batches.models import Batch
from apps.products.models import Category, Unit, Product
from apps.warehouses.models import Warehouse

User = get_user_model()


class PermissionsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = User.objects.create_user(
            phone='+998900001400', password='Test!',
            first_name='A', last_name='B', role='ADMIN',
        )
        self.katta = User.objects.create_user(
            phone='+998900001401', password='Test!',
            first_name='K', last_name='O', role='KATTA_OMBOR_ADMINI',
        )
        self.kichik = User.objects.create_user(
            phone='+998900001402', password='Test!',
            first_name='Ki', last_name='O', role='KICHIK_OMBOR_ADMINI',
        )
        self.hisobchi = User.objects.create_user(
            phone='+998900001403', password='Test!',
            first_name='H', last_name='U', role='HISOBCHI',
        )

    def _make_request(self, user):
        request = self.factory.get('/')
        request.user = user
        return request

    def test_is_admin(self):
        perm = IsAdmin()
        self.assertTrue(perm.has_permission(self._make_request(self.admin), None))
        self.assertFalse(perm.has_permission(self._make_request(self.katta), None))
        self.assertFalse(perm.has_permission(self._make_request(self.kichik), None))
        self.assertFalse(perm.has_permission(self._make_request(self.hisobchi), None))

    def test_is_admin_or_katta(self):
        perm = IsAdminOrKattaOmborAdmin()
        self.assertTrue(perm.has_permission(self._make_request(self.admin), None))
        self.assertTrue(perm.has_permission(self._make_request(self.katta), None))
        self.assertFalse(perm.has_permission(self._make_request(self.kichik), None))
        self.assertFalse(perm.has_permission(self._make_request(self.hisobchi), None))

    def test_is_admin_or_katta_or_kichik(self):
        perm = IsAdminOrKattaOrKichik()
        self.assertTrue(perm.has_permission(self._make_request(self.admin), None))
        self.assertTrue(perm.has_permission(self._make_request(self.katta), None))
        self.assertTrue(perm.has_permission(self._make_request(self.kichik), None))
        self.assertFalse(perm.has_permission(self._make_request(self.hisobchi), None))

    def test_is_admin_or_katta_or_hisobchi(self):
        perm = IsAdminOrKattaOrHisobchi()
        self.assertTrue(perm.has_permission(self._make_request(self.admin), None))
        self.assertTrue(perm.has_permission(self._make_request(self.katta), None))
        self.assertFalse(perm.has_permission(self._make_request(self.kichik), None))
        self.assertTrue(perm.has_permission(self._make_request(self.hisobchi), None))

    def test_can_manage_invoices(self):
        perm = CanManageInvoices()
        self.assertTrue(perm.has_permission(self._make_request(self.admin), None))
        self.assertTrue(perm.has_permission(self._make_request(self.katta), None))
        self.assertFalse(perm.has_permission(self._make_request(self.kichik), None))
        self.assertTrue(perm.has_permission(self._make_request(self.hisobchi), None))


class GenerateNumberTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test')
        self.unit = Unit.objects.create(name='Kg', abbreviation='kg')
        self.product = Product.objects.create(name='P', category=self.category, unit=self.unit)
        self.warehouse = Warehouse.objects.create(name='W', capacity=100)

    def test_first_number(self):
        num = generate_number('BATCH', Batch, 'batch_number')
        self.assertTrue(num.startswith('BATCH-'))
        self.assertTrue(num.endswith('0001'))

    def test_sequential_numbers(self):
        Batch.objects.create(
            product=self.product, warehouse=self.warehouse, unit=self.unit,
            quantity=10, price=100,
        )
        num = generate_number('BATCH', Batch, 'batch_number')
        self.assertTrue(num.endswith('0002'))

    def test_different_prefixes(self):
        num1 = generate_number('BATCH', Batch, 'batch_number')
        self.assertTrue(num1.startswith('BATCH-'))
