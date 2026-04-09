from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class LoginTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            phone='+998900000100', password='Test1234!',
            first_name='Test', last_name='User',
        )

    def test_login_success(self):
        resp = self.client.post('/api/auth/login/', {'phone': '+998900000100', 'password': 'Test1234!'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)

    def test_login_wrong_password(self):
        resp = self.client.post('/api/auth/login/', {'phone': '+998900000100', 'password': 'Wrong!'})
        self.assertIn(resp.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])

    def test_login_nonexistent_user(self):
        resp = self.client.post('/api/auth/login/', {'phone': '+998900000999', 'password': 'Test1234!'})
        self.assertIn(resp.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])


class TokenRefreshTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            phone='+998900000101', password='Test1234!',
            first_name='Test', last_name='User',
        )

    def test_token_refresh_success(self):
        login = self.client.post('/api/auth/login/', {'phone': '+998900000101', 'password': 'Test1234!'})
        resp = self.client.post('/api/auth/token/refresh/', {'refresh': login.data['refresh']})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)

    def test_token_refresh_invalid(self):
        resp = self.client.post('/api/auth/token/refresh/', {'refresh': 'invalid'})
        self.assertIn(resp.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])


class LogoutTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            phone='+998900000102', password='Test1234!',
            first_name='Test', last_name='User',
        )

    def test_logout_success(self):
        login = self.client.post('/api/auth/login/', {'phone': '+998900000102', 'password': 'Test1234!'})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        resp = self.client.post('/api/auth/logout/', {'refresh': login.data['refresh']})
        self.assertIn(resp.status_code, [status.HTTP_200_OK, status.HTTP_205_RESET_CONTENT])


class MeViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            phone='+998900000103', password='Test1234!',
            first_name='Test', last_name='User',
        )

    def test_me_authenticated(self):
        self.client.force_authenticate(self.user)
        resp = self.client.get('/api/auth/me/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['phone'], '+998900000103')

    def test_me_unauthenticated(self):
        resp = self.client.get('/api/auth/me/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class ChangePasswordTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            phone='+998900000104', password='OldPass1!',
            first_name='Test', last_name='User',
        )

    def test_change_password_success(self):
        self.client.force_authenticate(self.user)
        resp = self.client.put('/api/auth/change-password/', {
            'old_password': 'OldPass1!', 'new_password': 'NewPass1!',
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPass1!'))

    def test_change_password_wrong_old(self):
        self.client.force_authenticate(self.user)
        resp = self.client.put('/api/auth/change-password/', {
            'old_password': 'WrongOld!', 'new_password': 'NewPass1!',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class ForgotPasswordTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            phone='+998900000105', password='OldPass1!',
            first_name='Test', last_name='User',
        )

    def test_forgot_password_success(self):
        resp = self.client.post('/api/auth/forgot-password/', {
            'phone': '+998900000105', 'new_password': 'ResetPass1!',
        })
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('ResetPass1!'))

    def test_forgot_password_not_found(self):
        resp = self.client.post('/api/auth/forgot-password/', {
            'phone': '+998900000999', 'new_password': 'ResetPass1!',
        })
        self.assertIn(resp.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND])
