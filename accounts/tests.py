"""
Unit tests for the accounts app.

Tests user registration, authentication, and profile management functionality.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Profile


class UserModelTest(TestCase):
    """Test cases for User and Profile models."""
    
    def setUp(self):
        """Set up test data."""
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_creation(self):
        """Test that users are created correctly."""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertFalse(self.user.is_verified)
        self.assertTrue(self.user.is_active)

    def test_profile_creation(self):
        """Test that profiles are created correctly."""
        profile = Profile.objects.create(
            user=self.user,
            phone_number='1234567890',
            role='student'
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.phone_number, '1234567890')
        self.assertEqual(profile.role, 'student')
        self.assertEqual(profile.get_role_display_name(), 'Student')

    def test_user_string_representation(self):
        """Test user string representation."""
        self.assertEqual(str(self.user), 'test@example.com')

    def test_profile_string_representation(self):
        """Test profile string representation."""
        profile = Profile.objects.create(
            user=self.user,
            phone_number='1234567890',
            role='vendor'
        )
        self.assertEqual(str(profile), "testuser's profile")


class UserAPITest(APITestCase):
    """Test cases for API endpoints."""
    
    def setUp(self):
        """Set up test URLs."""
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.me_url = reverse('me')

    def test_user_registration_success(self):
        """Test successful user registration."""
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
        self.assertIn('message', response.data)
        
        # Verify user was created
        user = User.objects.get(email='newuser@example.com')
        self.assertEqual(user.username, 'newuser')
        self.assertTrue(user.profile.phone_number, '9876543210')

    def test_user_registration_missing_password_confirm(self):
        """Test registration fails when password_confirm is missing."""
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123',
            'profile': {
                'phone_number': '1234567890',
                'role': 'student'
            }
        }
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data['details'])

    def test_user_registration_password_mismatch(self):
        """Test registration fails when passwords don't match."""
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123',
            'password_confirm': 'differentpass',
            'profile': {
                'phone_number': '1234567890',
                'role': 'student'
            }
        }
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data['details'])

    def test_user_login_success(self):
        """Test successful user login."""
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
        self.assertIn('user', response.data)
        self.assertIn('message', response.data)

    def test_user_login_invalid_credentials(self):
        """Test login fails with invalid credentials."""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_me_endpoint_authenticated(self):
        """Test /me/ endpoint with authenticated user."""
        # Create and authenticate user
        user = User.objects.create_user(
            email='me@example.com',
            username='meuser',
            password='mepass123'
        )
        Profile.objects.create(
            user=user,
            phone_number='1111111111',
            role='admin'
        )
        
        # Get JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        # Make authenticated request
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'me@example.com')

    def test_me_endpoint_unauthenticated(self):
        """Test /me/ endpoint without authentication."""
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
