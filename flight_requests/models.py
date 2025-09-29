from django.db import models
from django.conf import settings
from django.utils import timezone
from destinations.models import Destination

class FlightRequest(models.Model):
    """
    Model representing a flight request made by a user
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('reserved', 'Reservada'),
        ('cancelled', 'Cancelada'),
        ('completed', 'Completada'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='flight_requests',
        help_text='Usuario que realiza la solicitud'
    )
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name='flight_requests',
        help_text='Destino del vuelo'
    )
    travel_date = models.DateField(
        help_text='Fecha del viaje'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Estado de la solicitud'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Notas adicionales del usuario'
    )
    operator_notes = models.TextField(
        blank=True,
        null=True,
        help_text='Notas del operador'
    )
    reserved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reserved_flights',
        help_text='Operador que reservó el vuelo'
    )
    reserved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha y hora de reserva'
    )
    notification_sent = models.BooleanField(
        default=False,
        help_text='Indica si se envió la notificación de recordatorio'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Solicitud de Vuelo'
        verbose_name_plural = 'Solicitudes de Vuelo'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.destination.name} ({self.travel_date})"
    
    def save(self, *args, **kwargs):
        # Check if this is a new reservation
        is_new_reservation = False
        if self.pk:
            old_instance = FlightRequest.objects.get(pk=self.pk)
            is_new_reservation = (old_instance.status != 'reserved' and self.status == 'reserved')
        else:
            is_new_reservation = self.status == 'reserved'
        
        if self.status == 'reserved' and not self.reserved_at:
            self.reserved_at = timezone.now()
        
        super().save(*args, **kwargs)
        
        # Send confirmation email for new reservations
        if is_new_reservation:
            from .tasks import send_reservation_confirmation
            send_reservation_confirmation.delay(self.id)
    
    @property
    def is_pending(self):
        return self.status == 'pending'
    
    @property
    def is_reserved(self):
        return self.status == 'reserved'
    
    @property
    def days_until_travel(self):
        """Calculate days until travel date"""
        if self.travel_date:
            delta = self.travel_date - timezone.now().date()
            return delta.days
        return None
    
    @property
    def needs_notification(self):
        """Check if notification should be sent (2 days before travel)"""
        return (
            self.is_reserved and 
            not self.notification_sent and 
            self.days_until_travel == 2
        )
