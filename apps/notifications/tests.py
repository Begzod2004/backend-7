from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.notifications.models import Notification

User = get_user_model()


class NotificationModelTest(TestCase):
    def test_create_notification(self):
        n = Notification.objects.create(
            type='LOW_STOCK', title='Kam zaxira',
            message='Armatura kam qoldi',
        )
        self.assertEqual(n.type, 'LOW_STOCK')
        self.assertFalse(n.is_read)

    def test_notification_with_user(self):
        user = User.objects.create_user(
            phone='+998900001200', password='Test!', first_name='A', last_name='B',
        )
        n = Notification.objects.create(
            type='SYSTEM', title='Tizim', message='Test', user=user,
        )
        self.assertEqual(n.user, user)


class NotificationAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            phone='+998900001210', password='Admin1234!',
            first_name='Admin', last_name='User', role='ADMIN',
        )

    def test_list_notifications(self):
        Notification.objects.create(type='SYSTEM', title='Test', message='Hello')
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/notifications/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_mark_read(self):
        n = Notification.objects.create(type='SYSTEM', title='Test', message='Hello')
        self.client.force_authenticate(self.admin)
        resp = self.client.put(f'/api/notifications/{n.id}/read/')
        self.assertIn(resp.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        n.refresh_from_db()
        self.assertTrue(n.is_read)

    def test_mark_all_read(self):
        Notification.objects.create(type='SYSTEM', title='T1', message='M1')
        Notification.objects.create(type='LOW_STOCK', title='T2', message='M2')
        self.client.force_authenticate(self.admin)
        resp = self.client.put('/api/notifications/read-all/')
        self.assertIn(resp.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])

    def test_unauthenticated_cannot_access(self):
        resp = self.client.get('/api/notifications/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
