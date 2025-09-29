from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from destinations.models import Destination
from flight_requests.models import FlightRequest

User = get_user_model()

class AuthAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.logout_url = '/api/auth/logout/'
        self.profile_url = '/api/auth/profile/'
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'client'
        }

    def test_user_registration(self):
        """Test user registration"""
        response = self.client.post(self.register_url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('token', response.data)
        
        # Check user was created
        user = User.objects.get(email=self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])

    def test_user_registration_password_mismatch(self):
        """Test registration with password mismatch"""
        data = self.user_data.copy()
        data['password_confirm'] = 'different'
        
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login(self):
        """Test user login"""
        # Create user first
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIn('token', response.data)

    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class DestinationAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.destinations_url = '/api/destinations/destinations/'
        self.active_destinations_url = '/api/destinations/destinations/active_destinations/'
        
        # Create users
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            role='admin'
        )
        
        self.client_user = User.objects.create_user(
            username='client',
            email='client@example.com',
            password='clientpass123',
            role='client'
        )
        
        # Create test destination
        self.destination = Destination.objects.create(
            name='Quito',
            code='UIO',
            description='Capital del Ecuador',
            is_active=True
        )

    def test_get_active_destinations_authenticated(self):
        """Test getting active destinations as authenticated user"""
        self.client.force_authenticate(user=self.client_user)
        
        response = self.client.get(self.active_destinations_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_get_active_destinations_unauthenticated(self):
        """Test getting active destinations without authentication"""
        response = self.client.get(self.active_destinations_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_destination_as_admin(self):
        """Test creating destination as admin"""
        self.client.force_authenticate(user=self.admin_user)
        
        data = {
            'name': 'Guayaquil',
            'code': 'GYE',
            'description': 'Puerto Principal',
            'is_active': True
        }
        
        response = self.client.post(self.destinations_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Guayaquil')

    def test_create_destination_as_client_forbidden(self):
        """Test that clients cannot create destinations"""
        self.client.force_authenticate(user=self.client_user)
        
        data = {
            'name': 'Guayaquil',
            'code': 'GYE',
            'description': 'Puerto Principal',
            'is_active': True
        }
        
        response = self.client.post(self.destinations_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class FlightRequestAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.flight_requests_url = '/api/flight-requests/flight-requests/'
        self.pending_url = '/api/flight-requests/flight-requests/pending/'
        
        # Create users
        self.client_user = User.objects.create_user(
            username='client',
            email='client@example.com',
            password='clientpass123',
            role='client'
        )
        
        self.operator_user = User.objects.create_user(
            username='operator',
            email='operator@example.com',
            password='operatorpass123',
            role='operator'
        )
        
        # Create destination
        self.destination = Destination.objects.create(
            name='Quito',
            code='UIO',
            is_active=True
        )

    def test_create_flight_request(self):
        """Test creating a flight request"""
        self.client.force_authenticate(user=self.client_user)
        
        data = {
            'destination': self.destination.id,
            'travel_date': (date.today() + timedelta(days=7)).isoformat(),
            'notes': 'Test flight request'
        }
        
        response = self.client.post(self.flight_requests_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['id'], self.client_user.id)
        self.assertEqual(response.data['destination']['id'], self.destination.id)

    def test_create_flight_request_past_date(self):
        """Test creating flight request with past date fails"""
        self.client.force_authenticate(user=self.client_user)
        
        data = {
            'destination': self.destination.id,
            'travel_date': (date.today() - timedelta(days=1)).isoformat(),
            'notes': 'Test flight request'
        }
        
        response = self.client.post(self.flight_requests_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_pending_requests_as_operator(self):
        """Test getting pending requests as operator"""
        # Create a pending request
        FlightRequest.objects.create(
            user=self.client_user,
            destination=self.destination,
            travel_date=date.today() + timedelta(days=7),
            status='pending'
        )
        
        self.client.force_authenticate(user=self.operator_user)
        
        response = self.client.get(self.pending_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_get_pending_requests_as_client_forbidden(self):
        """Test that clients cannot see pending requests"""
        self.client.force_authenticate(user=self.client_user)
        
        response = self.client.get(self.pending_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reserve_flight_request(self):
        """Test reserving a flight request"""
        flight_request = FlightRequest.objects.create(
            user=self.client_user,
            destination=self.destination,
            travel_date=date.today() + timedelta(days=7),
            status='pending'
        )
        
        self.client.force_authenticate(user=self.operator_user)
        
        reserve_url = f'{self.flight_requests_url}{flight_request.id}/reserve/'
        data = {'operator_notes': 'Approved by operator'}
        
        response = self.client.post(reserve_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'reserved')
        
        # Check in database
        flight_request.refresh_from_db()
        self.assertEqual(flight_request.status, 'reserved')
        self.assertEqual(flight_request.reserved_by, self.operator_user)