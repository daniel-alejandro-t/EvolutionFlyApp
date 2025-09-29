from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta
from unittest.mock import patch, MagicMock
from users.models import User
from destinations.models import Destination
from flight_requests.models import FlightRequest
from flight_requests.tasks import (
    send_flight_reminder_notification,
    check_and_send_flight_reminders,
    send_reservation_confirmation
)

class CeleryTasksTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create test destination
        self.destination = Destination.objects.create(
            name='Quito',
            code='UIO',
            is_active=True
        )
        
        # Create test flight request
        self.flight_request = FlightRequest.objects.create(
            user=self.user,
            destination=self.destination,
            travel_date=date.today() + timedelta(days=2),
            status='reserved'
        )

    @patch('flight_requests.tasks.send_mail')
    def test_send_flight_reminder_notification_success(self, mock_send_mail):
        """Test successful flight reminder notification"""
        result = send_flight_reminder_notification(self.flight_request.id)
        
        # Check that email was sent
        mock_send_mail.assert_called_once()
        
        # Check that notification was marked as sent
        self.flight_request.refresh_from_db()
        self.assertTrue(self.flight_request.notification_sent)
        
        # Check return value
        self.assertIn(f"Notification sent to {self.user.email}", result)

    @patch('flight_requests.tasks.send_mail')
    def test_send_flight_reminder_already_sent(self, mock_send_mail):
        """Test that reminder is not sent if already sent"""
        # Mark as already sent
        self.flight_request.notification_sent = True
        self.flight_request.save()
        
        result = send_flight_reminder_notification(self.flight_request.id)
        
        # Email should not be sent
        mock_send_mail.assert_not_called()
        
        # Check log message
        self.assertIn(f"Notification already sent for flight request {self.flight_request.id}", result)

    @patch('flight_requests.tasks.send_mail')
    def test_send_flight_reminder_not_reserved(self, mock_send_mail):
        """Test that reminder is not sent for non-reserved flights"""
        # Change status to pending
        self.flight_request.status = 'pending'
        self.flight_request.save()
        
        result = send_flight_reminder_notification(self.flight_request.id)
        
        # Email should not be sent
        mock_send_mail.assert_not_called()
        
        # Check log message
        self.assertIn(f"Flight request {self.flight_request.id} is not reserved", result)

    @patch('flight_requests.tasks.send_mail')
    def test_send_flight_reminder_wrong_timing(self, mock_send_mail):
        """Test that reminder is not sent if not 2 days before"""
        # Change travel date to 5 days from now
        self.flight_request.travel_date = date.today() + timedelta(days=5)
        self.flight_request.save()
        
        result = send_flight_reminder_notification(self.flight_request.id)
        
        # Email should not be sent
        mock_send_mail.assert_not_called()
        
        # Check log message
        self.assertIn(f"Flight request {self.flight_request.id} is 5 days away, not 2 days", result)

    def test_send_flight_reminder_nonexistent_request(self):
        """Test handling of nonexistent flight request"""
        result = send_flight_reminder_notification(99999)
        
        self.assertIn("Flight request 99999 not found", result)

    @patch('flight_requests.tasks.send_flight_reminder_notification')
    def test_check_and_send_flight_reminders(self, mock_send_reminder):
        """Test the periodic task that checks for reminders"""
        # Create multiple flight requests
        target_date = date.today() + timedelta(days=2)
        
        # Request that needs reminder
        request1 = FlightRequest.objects.create(
            user=self.user,
            destination=self.destination,
            travel_date=target_date,
            status='reserved',
            notification_sent=False
        )
        
        # Request already notified
        request2 = FlightRequest.objects.create(
            user=self.user,
            destination=self.destination,
            travel_date=target_date,
            status='reserved',
            notification_sent=True
        )
        
        # Request not reserved
        request3 = FlightRequest.objects.create(
            user=self.user,
            destination=self.destination,
            travel_date=target_date,
            status='pending',
            notification_sent=False
        )
        
        result = check_and_send_flight_reminders()
        
        # Should only call for request1
        mock_send_reminder.delay.assert_called_once_with(request1.id)
        
        self.assertIn("Queued 1 notifications", result)

    @patch('flight_requests.tasks.send_mail')
    def test_send_reservation_confirmation(self, mock_send_mail):
        """Test sending reservation confirmation email"""
        result = send_reservation_confirmation(self.flight_request.id)
        
        # Check that email was sent
        mock_send_mail.assert_called_once()
        
        # Check return value
        self.assertIn(f"Confirmation sent to {self.user.email}", result)

    @patch('flight_requests.tasks.send_mail', side_effect=Exception('SMTP Error'))
    def test_send_flight_reminder_email_failure(self, mock_send_mail):
        """Test handling of email sending failure"""
        with self.assertRaises(Exception):
            send_flight_reminder_notification(self.flight_request.id)
        
        # Notification should not be marked as sent
        self.flight_request.refresh_from_db()
        self.assertFalse(self.flight_request.notification_sent)