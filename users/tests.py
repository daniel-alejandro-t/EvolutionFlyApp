import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from users.models import User

class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123'
        }

    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'client')  # Default role
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test creating a superuser"""
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)

    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(**self.user_data)
        expected = f"{user.get_full_name()} ({user.email})"
        self.assertEqual(str(user), expected)

    def test_user_roles(self):
        """Test user role methods"""
        # Test client
        client = User.objects.create_user(role='client', **self.user_data)
        self.assertTrue(client.is_client())
        self.assertFalse(client.is_operator())
        self.assertFalse(client.is_admin_user())

        # Test operator
        operator_data = self.user_data.copy()
        operator_data['username'] = 'operator'
        operator_data['email'] = 'operator@example.com'
        operator = User.objects.create_user(role='operator', **operator_data)
        self.assertFalse(operator.is_client())
        self.assertTrue(operator.is_operator())
        self.assertFalse(operator.is_admin_user())

        # Test admin
        admin_data = self.user_data.copy()
        admin_data['username'] = 'admin'
        admin_data['email'] = 'admin@example.com'
        admin = User.objects.create_user(role='admin', **admin_data)
        self.assertFalse(admin.is_client())
        self.assertFalse(admin.is_operator())
        self.assertTrue(admin.is_admin_user())

    def test_unique_email(self):
        """Test that email must be unique"""
        User.objects.create_user(**self.user_data)
        
        duplicate_data = self.user_data.copy()
        duplicate_data['username'] = 'different'
        
        with self.assertRaises(Exception):
            User.objects.create_user(**duplicate_data)
