from rest_framework import serializers
from django.utils import timezone
from .models import FlightRequest
from destinations.serializers import DestinationListSerializer
from users.serializers import UserSerializer

class FlightRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlightRequest
        fields = ('destination', 'travel_date', 'notes')
    
    def validate_travel_date(self, value):
        if value <= timezone.now().date():
            raise serializers.ValidationError(
                "La fecha de viaje debe ser futura"
            )
        return value
    
    def create(self, validated_data):
        # El usuario se asigna automáticamente desde la vista
        return super().create(validated_data)

class FlightRequestSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    destination = DestinationListSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    days_until_travel = serializers.ReadOnlyField()
    
    class Meta:
        model = FlightRequest
        fields = (
            'id', 'user', 'destination', 'travel_date', 'status', 'status_display',
            'notes', 'operator_notes', 'reserved_by', 'reserved_at',
            'days_until_travel', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'user', 'reserved_by', 'reserved_at', 'created_at', 'updated_at'
        )

class FlightRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlightRequest
        fields = ('status', 'operator_notes')
    
    def validate_status(self, value):
        if self.instance and self.instance.status == 'completed':
            raise serializers.ValidationError(
                "No se puede modificar una solicitud completada"
            )
        return value