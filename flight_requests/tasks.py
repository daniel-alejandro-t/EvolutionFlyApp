from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from .models import FlightRequest
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_flight_reminder_notification(flight_request_id):
    """
    Send reminder notification 2 days before flight
    """
    try:
        flight_request = FlightRequest.objects.get(id=flight_request_id)
        
        if flight_request.notification_sent:
            logger.info(f"Notification already sent for flight request {flight_request_id}")
            return
        
        # Check if flight is still reserved and 2 days away
        if not flight_request.is_reserved:
            logger.info(f"Flight request {flight_request_id} is not reserved, skipping notification")
            return
        
        days_until_travel = flight_request.days_until_travel
        if days_until_travel != 2:
            logger.info(f"Flight request {flight_request_id} is {days_until_travel} days away, not 2 days")
            return
        
        # Prepare email content
        subject = f'Recordatorio: Tu vuelo a {flight_request.destination.name} es en 2 días'
        
        context = {
            'user': flight_request.user,
            'flight_request': flight_request,
            'travel_date': flight_request.travel_date,
            'destination': flight_request.destination,
        }
        
        html_message = render_to_string('emails/flight_reminder.html', context)
        plain_message = render_to_string('emails/flight_reminder.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[flight_request.user.email],
            fail_silently=False,
        )
        
        # Mark notification as sent
        flight_request.notification_sent = True
        flight_request.save(update_fields=['notification_sent'])
        
        logger.info(f"Reminder notification sent successfully for flight request {flight_request_id}")
        return f"Notification sent to {flight_request.user.email}"
        
    except FlightRequest.DoesNotExist:
        logger.error(f"Flight request {flight_request_id} not found")
        return f"Flight request {flight_request_id} not found"
    except Exception as e:
        logger.error(f"Error sending notification for flight request {flight_request_id}: {str(e)}")
        raise

@shared_task
def check_and_send_flight_reminders():
    """
    Periodic task to check all flight requests that need reminders
    """
    try:
        # Get all reserved flights that need notification (2 days before travel)
        today = timezone.now().date()
        target_date = today + timezone.timedelta(days=2)
        
        flight_requests = FlightRequest.objects.filter(
            status='reserved',
            travel_date=target_date,
            notification_sent=False
        )
        
        count = 0
        for flight_request in flight_requests:
            send_flight_reminder_notification.delay(flight_request.id)
            count += 1
        
        logger.info(f"Queued {count} flight reminder notifications")
        return f"Queued {count} notifications"
        
    except Exception as e:
        logger.error(f"Error in check_and_send_flight_reminders: {str(e)}")
        raise

@shared_task
def send_reservation_confirmation(flight_request_id):
    """
    Send confirmation email when flight is reserved
    """
    try:
        flight_request = FlightRequest.objects.get(id=flight_request_id)
        
        subject = f'Confirmación: Tu vuelo a {flight_request.destination.name} ha sido reservado'
        
        context = {
            'user': flight_request.user,
            'flight_request': flight_request,
            'reserved_by': flight_request.reserved_by,
            'reserved_at': flight_request.reserved_at,
        }
        
        html_message = render_to_string('emails/reservation_confirmation.html', context)
        plain_message = render_to_string('emails/reservation_confirmation.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[flight_request.user.email],
            fail_silently=False,
        )
        
        logger.info(f"Reservation confirmation sent for flight request {flight_request_id}")
        return f"Confirmation sent to {flight_request.user.email}"
        
    except Exception as e:
        logger.error(f"Error sending reservation confirmation for {flight_request_id}: {str(e)}")
        raise