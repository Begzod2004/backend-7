from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.products.models import Category, Unit, Product
from apps.warehouses.models import Warehouse
from apps.orders.models import Order, OrderItem, OrderStatusHistory

User = get_user_model()


class OrderModelTest(TestCase):
    def setUp(self):
        self.warehouse = Warehouse.objects.create(name='Markaziy', capacity=10000)
        self.admin = User.objects.create_user(
            phone='+998900000500', password='Test!', first_name='A', last_name='B', role='ADMIN',
        )

    def test_auto_order_number(self):
        order = Order.objects.create(
            type='INCOMING', warehouse=self.warehouse, created_by=self.admin,
        )
        self.assertTrue(order.order_number.startswith('ORD-'))

    def test_default_status(self):
        order = Order.objects.create(
            type='INCOMING', warehouse=self.warehouse, created_by=self.admin,
        )
        self.assertEqual(order.status, 'NEW')

    def test_calculate_total(self):
        category = Category.objects.create(name='Test')
        unit = Unit.objects.create(name='Dona', abbreviation='ta')
        product = Product.objects.create(name='P1', category=category, unit=unit, price=1000)
        order = Order.objects.create(
            type='INCOMING', warehouse=self.warehouse, created_by=self.admin,
        )
        OrderItem.objects.create(order=order, product=product, quantity=10, price=1000)
        OrderItem.objects.create(order=order, product=product, quantity=5, price=2000)
        order.calculate_total()
        order.refresh_from_db()
        self.assertEqual(order.total_amount, 10 * 1000 + 5 * 2000)


class OrderAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            phone='+998900000510', password='Admin1234!',
            first_name='Admin', last_name='User', role='ADMIN',
        )
        self.warehouse = Warehouse.objects.create(name='Markaziy', capacity=10000)
        self.category = Category.objects.create(name='Metall')
        self.unit = Unit.objects.create(name='Kg', abbreviation='kg')
        self.product = Product.objects.create(name='Armatura', category=self.category, unit=self.unit, price=15000)

    def test_create_order(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.post('/api/orders/', {
            'type': 'INCOMING',
            'warehouse': self.warehouse.id,
            'customer_name': 'Test Customer',
            'items': [
                {'product': self.product.id, 'quantity': 10, 'price': 15000},
            ],
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        order = Order.objects.last()
        self.assertTrue(order.order_number.startswith('ORD-'))

    def test_list_orders(self):
        Order.objects.create(type='INCOMING', warehouse=self.warehouse, created_by=self.admin)
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/orders/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_update_status(self):
        order = Order.objects.create(type='INCOMING', warehouse=self.warehouse, created_by=self.admin)
        self.client.force_authenticate(self.admin)
        resp = self.client.put(f'/api/orders/{order.id}/status/', {
            'status': 'PROCESSING', 'note': 'Jarayonda',
        })
        self.assertIn(resp.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        order.refresh_from_db()
        self.assertEqual(order.status, 'PROCESSING')
        self.assertTrue(OrderStatusHistory.objects.filter(order=order, status='PROCESSING').exists())

    def test_filter_by_type(self):
        Order.objects.create(type='INCOMING', warehouse=self.warehouse, created_by=self.admin)
        Order.objects.create(type='OUTGOING', warehouse=self.warehouse, created_by=self.admin)
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/orders/?type=INCOMING')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
