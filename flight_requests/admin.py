from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import FlightRequest

@admin.register(FlightRequest)
class FlightRequestAdmin(admin.ModelAdmin):
    list_display = (
        'user_info', 'destination', 'travel_date', 'status_display', 
        'reserved_by', 'days_until_travel_display', 'created_at'
    )
    list_filter = ('status', 'travel_date', 'created_at', 'destination')
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'destination__name', 'destination__code'
    )
    ordering = ('-created_at',)
    date_hierarchy = 'travel_date'
    
    fieldsets = (
        ('Información del Solicitante', {
            'fields': ('user', 'destination', 'travel_date', 'notes')
        }),
        ('Estado de la Solicitud', {
            'fields': ('status', 'reserved_by', 'reserved_at', 'operator_notes')
        }),
        ('Notificaciones', {
            'fields': ('notification_sent',),
            'classes': ('collapse',)
        }),
        ('Información de Seguimiento', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'reserved_at')
    
    actions = ['mark_as_reserved', 'mark_as_cancelled', 'mark_as_completed']
    
    def user_info(self, obj):
        return f"{obj.user.get_full_name()} ({obj.user.email})"
    user_info.short_description = 'Usuario'
    
    def status_display(self, obj):
        colors = {
            'pending': '#ffc107',
            'reserved': '#28a745', 
            'cancelled': '#dc3545',
            'completed': '#6c757d'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Estado'
    
    def days_until_travel_display(self, obj):
        days = obj.days_until_travel
        if days is None:
            return '-'
        elif days < 0:
            return format_html('<span style="color: #dc3545;">Pasado</span>')
        elif days == 0:
            return format_html('<span style="color: #ffc107;">Hoy</span>')
        elif days <= 2:
            return format_html('<span style="color: #fd7e14;">{} días</span>', days)
        else:
            return f'{days} días'
    days_until_travel_display.short_description = 'Días restantes'
    
    def mark_as_reserved(self, request, queryset):
        updated = 0
        for flight_request in queryset.filter(status='pending'):
            flight_request.status = 'reserved'
            flight_request.reserved_by = request.user
            flight_request.save()
            updated += 1
        self.message_user(request, f'{updated} solicitudes marcadas como reservadas.')
    mark_as_reserved.short_description = 'Marcar como reservadas'
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} solicitudes canceladas.')
    mark_as_cancelled.short_description = 'Cancelar solicitudes'
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} solicitudes completadas.')
    mark_as_completed.short_description = 'Marcar como completadas'
