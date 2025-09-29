from django.db import models
from django.core.cache import cache

class Destination(models.Model):
    """
    Model representing flight destinations (cities in Ecuador)
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text='Nombre de la ciudad'
    )
    code = models.CharField(
        max_length=3,
        unique=True,
        help_text='Código IATA de la ciudad'
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Descripción de la ciudad'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Indica si el destino está disponible'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Destino'
        verbose_name_plural = 'Destinos'
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Clear cache when destination is modified
        cache.delete('destinations_list')
    
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        # Clear cache when destination is deleted
        cache.delete('destinations_list')
    
    @classmethod
    def get_active_destinations(cls):
        """
        Get all active destinations from cache or database
        """
        cache_key = 'destinations_list'
        destinations = cache.get(cache_key)
        
        if destinations is None:
            destinations = list(cls.objects.filter(is_active=True).values(
                'id', 'name', 'code', 'description'
            ))
            cache.set(cache_key, destinations, timeout=3600)  # Cache for 1 hour
            
        return destinations
