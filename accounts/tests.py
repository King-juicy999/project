from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User, Profile


class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertFalse(self.user.is_verified)

    def test_profile_creation(self):
        profile = Profile.objects.create(
            user=self.user,
            phone_number='1234567890',
            role='student'
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.phone_number, '1234567890')
        self.assertEqual(profile.role, 'student')


class UserAPITest(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.me_url = reverse('me')

    def test_user_registration(self):
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'profile': {
                'phone_number': '9876543210',
                'role': 'student',
                'date_of_birth': '1990-01-01'
            }
        }
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)

    def test_user_login(self):
        # Create a user first
        user = User.objects.create_user(
            email='login@example.com',
            username='loginuser',
            password='loginpass123'
        )
        Profile.objects.create(
            user=user,
            phone_number='5555555555',
            role='vendor'
        )
        
        data = {
            'email': 'login@example.com',
            'password': 'loginpass123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
