from rest_framework import serializers
from .models import Destination

class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = ('id', 'name', 'code', 'description', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class DestinationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing destinations"""
    class Meta:
        model = Destination
        fields = ('id', 'name', 'code', 'description')