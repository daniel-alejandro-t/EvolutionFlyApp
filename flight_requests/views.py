from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import FlightRequest
from .serializers import (
    FlightRequestCreateSerializer, FlightRequestSerializer, 
    FlightRequestUpdateSerializer
)

class IsOwnerOrOperator(permissions.BasePermission):
    """
    Custom permission to allow users to see their own requests
    and operators to see all requests.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for owner or operators
        if request.method in permissions.SAFE_METHODS:
            return obj.user == request.user or request.user.is_operator() or request.user.is_admin_user()
        
        # Write permissions only for operators and admins
        if view.action in ['reserve', 'update']:
            return request.user.is_operator() or request.user.is_admin_user()
        
        # Only owners can update their own requests (limited fields)
        return obj.user == request.user

class FlightRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing flight requests
    """
    serializer_class = FlightRequestSerializer
    permission_classes = [IsOwnerOrOperator]
    
    def get_queryset(self):
        """
        Filter queryset based on user role
        """
        user = self.request.user
        if user.is_operator() or user.is_admin_user():
            return FlightRequest.objects.all()
        return FlightRequest.objects.filter(user=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FlightRequestCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return FlightRequestUpdateSerializer
        return FlightRequestSerializer
    
    def perform_create(self, serializer):
        """
        Save the user when creating a flight request
        """
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        """
        Handle reservation logic when updating
        """
        if serializer.validated_data.get('status') == 'reserved':
            serializer.save(
                reserved_by=self.request.user,
                reserved_at=timezone.now()
            )
        else:
            serializer.save()
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """
        Get all pending flight requests (for operators)
        """
        if not (request.user.is_operator() or request.user.is_admin_user()):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        pending_requests = FlightRequest.objects.filter(status='pending')
        serializer = self.get_serializer(pending_requests, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reserve(self, request, pk=None):
        """
        Reserve a pending flight request
        """
        if not (request.user.is_operator() or request.user.is_admin_user()):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        flight_request = self.get_object()
        
        if flight_request.status != 'pending':
            return Response(
                {'error': 'Solo se pueden reservar solicitudes pendientes'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        flight_request.status = 'reserved'
        flight_request.reserved_by = request.user
        flight_request.reserved_at = timezone.now()
        flight_request.operator_notes = request.data.get('operator_notes', '')
        flight_request.save()
        
        serializer = self.get_serializer(flight_request)
        return Response(serializer.data)
