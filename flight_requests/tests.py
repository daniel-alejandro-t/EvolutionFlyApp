from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta
from unittest.mock import patch
from users.models import User
from destinations.models import Destination
from flight_requests.models import FlightRequest

class FlightRequestModelTest(TestCase):
    def setUp(self):
        # Create test users
        self.client = User.objects.create_user(
            username='client',
            email='client@example.com',
            password='testpass123',
            first_name='John',
            last_name='Client',
            role='client'
        )
        
        self.operator = User.objects.create_user(
            username='operator',
            email='operator@example.com',
            password='testpass123',
            first_name='Jane',
            last_name='Operator',
            role='operator'
        )
        
        # Create test destination
        self.destination = Destination.objects.create(
            name='Quito',
            code='UIO',
            description='Capital del Ecuador',
            is_active=True
        )
        
        self.flight_request_data = {
            'user': self.client,
            'destination': self.destination,
            'travel_date': date.today() + timedelta(days=7),
            'notes': 'Test flight request'
        }

    def test_create_flight_request(self):
        """Test creating a flight request"""
        flight_request = FlightRequest.objects.create(**self.flight_request_data)
        
        self.assertEqual(flight_request.user, self.client)
        self.assertEqual(flight_request.destination, self.destination)
        self.assertEqual(flight_request.status, 'pending')
        self.assertFalse(flight_request.notification_sent)

    def test_flight_request_str_representation(self):
        """Test flight request string representation"""
        flight_request = FlightRequest.objects.create(**self.flight_request_data)
        expected = f"{self.client.get_full_name()} - {self.destination.name} ({flight_request.travel_date})"
        self.assertEqual(str(flight_request), expected)

    def test_status_properties(self):
        """Test status property methods"""
        flight_request = FlightRequest.objects.create(**self.flight_request_data)
        
        # Test pending status
        self.assertTrue(flight_request.is_pending)
        self.assertFalse(flight_request.is_reserved)
        
        # Change to reserved
        flight_request.status = 'reserved'
        flight_request.save()
        
        self.assertFalse(flight_request.is_pending)
        self.assertTrue(flight_request.is_reserved)

    def test_days_until_travel(self):
        """Test days until travel calculation"""
        # Future date
        future_date = date.today() + timedelta(days=5)
        flight_request = FlightRequest.objects.create(
            user=self.client,
            destination=self.destination,
            travel_date=future_date
        )
        
        self.assertEqual(flight_request.days_until_travel, 5)
        
        # Past date
        past_date = date.today() - timedelta(days=2)
        flight_request.travel_date = past_date
        flight_request.save()
        
        self.assertEqual(flight_request.days_until_travel, -2)

    def test_needs_notification(self):
        """Test needs notification property"""
        # Create reserved flight 2 days in future
        travel_date = date.today() + timedelta(days=2)
        flight_request = FlightRequest.objects.create(
            user=self.client,
            destination=self.destination,
            travel_date=travel_date,
            status='reserved'
        )
        
        self.assertTrue(flight_request.needs_notification)
        
        # Already notified
        flight_request.notification_sent = True
        flight_request.save()
        
        self.assertFalse(flight_request.needs_notification)
        
        # Not reserved
        flight_request.status = 'pending'
        flight_request.notification_sent = False
        flight_request.save()
        
        self.assertFalse(flight_request.needs_notification)

    @patch('flight_requests.tasks.send_reservation_confirmation')
    def test_reservation_triggers_notification(self, mock_send_confirmation):
        """Test that changing status to reserved triggers notification"""
        flight_request = FlightRequest.objects.create(**self.flight_request_data)
        
        # Change to reserved
        flight_request.status = 'reserved'
        flight_request.reserved_by = self.operator
        flight_request.save()
        
        # Check that reserved_at was set
        self.assertIsNotNone(flight_request.reserved_at)
        
        # Check that notification task was called
        mock_send_confirmation.delay.assert_called_once_with(flight_request.id)

    def test_save_sets_reserved_at(self):
        """Test that saving with reserved status sets reserved_at"""
        flight_request = FlightRequest.objects.create(**self.flight_request_data)
        
        # Initially no reserved_at
        self.assertIsNone(flight_request.reserved_at)
        
        # Change to reserved
        flight_request.status = 'reserved'
        flight_request.save()
        
        # Now should have reserved_at
        self.assertIsNotNone(flight_request.reserved_at)
