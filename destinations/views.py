from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from .models import Destination
from .serializers import DestinationSerializer

class DestinationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing destinations
    """
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """Solo admins pueden crear, actualizar y eliminar destinos"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated]  # Aquí podrías agregar IsAdminUser
        return super().get_permissions()

    @action(detail=False, methods=['get'], url_path='active-destinations')
    def active_destinations(self, request):
        """Endpoint para obtener destinos activos (con cache)"""
        cache_key = 'active_destinations'
        destinations = cache.get(cache_key)
        
        if not destinations:
            destinations = Destination.objects.filter(is_active=True).order_by('name')
            serializer = self.get_serializer(destinations, many=True)
            destinations_data = serializer.data
            cache.set(cache_key, destinations_data, 300)  # 5 minutos de cache
            return Response(destinations_data)
        
        return Response(destinations)

    def list(self, request, *args, **kwargs):
        """Override list para usar cache"""
        cache_key = 'all_destinations'
        destinations = cache.get(cache_key)
        
        if not destinations:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            destinations = serializer.data
            cache.set(cache_key, destinations, 300)  # 5 minutos de cache
        
        return Response(destinations)
