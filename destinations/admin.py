from django.contrib import admin
from .models import Destination

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    ordering = ('name',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'description', 'is_active')
        }),
        ('Información de Seguimiento', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    actions = ['activate_destinations', 'deactivate_destinations']
    
    def activate_destinations(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} destinos activados correctamente.')
    activate_destinations.short_description = 'Activar destinos seleccionados'
    
    def deactivate_destinations(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} destinos desactivados correctamente.')
    deactivate_destinations.short_description = 'Desactivar destinos seleccionados'
