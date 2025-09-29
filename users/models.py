from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User model with role-based access
    """
    
    ROLE_CHOICES = [
        ('client', 'Cliente'),
        ('operator', 'Operador'),
        ('admin', 'Administrador'),
    ]
    
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='client',
        help_text='Rol del usuario en el sistema'
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text='Número de teléfono del usuario'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def is_client(self):
        return self.role == 'client'
    
    def is_operator(self):
        return self.role == 'operator'
    
    def is_admin_user(self):
        return self.role == 'admin' or self.is_superuser
