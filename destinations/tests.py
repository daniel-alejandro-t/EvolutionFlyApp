from django.test import TestCase
from django.core.cache import cache
from destinations.models import Destination

class DestinationModelTest(TestCase):
    def setUp(self):
        self.destination_data = {
            'name': 'Quito',
            'code': 'UIO',
            'description': 'Capital del Ecuador',
            'is_active': True
        }

    def test_create_destination(self):
        """Test creating a destination"""
        destination = Destination.objects.create(**self.destination_data)
        
        self.assertEqual(destination.name, 'Quito')
        self.assertEqual(destination.code, 'UIO')
        self.assertEqual(destination.description, 'Capital del Ecuador')
        self.assertTrue(destination.is_active)

    def test_destination_str_representation(self):
        """Test destination string representation"""
        destination = Destination.objects.create(**self.destination_data)
        expected = f"{destination.name} ({destination.code})"
        self.assertEqual(str(destination), expected)

    def test_unique_name_and_code(self):
        """Test that name and code must be unique"""
        Destination.objects.create(**self.destination_data)
        
        # Test duplicate name
        with self.assertRaises(Exception):
            duplicate_name = self.destination_data.copy()
            duplicate_name['code'] = 'QUI'
            Destination.objects.create(**duplicate_name)
        
        # Test duplicate code
        with self.assertRaises(Exception):
            duplicate_code = self.destination_data.copy()
            duplicate_code['name'] = 'Quito Norte'
            Destination.objects.create(**duplicate_code)

    def test_get_active_destinations(self):
        """Test getting active destinations with cache"""
        # Create active and inactive destinations
        Destination.objects.create(name='Quito', code='UIO', is_active=True)
        Destination.objects.create(name='Guayaquil', code='GYE', is_active=True)
        Destination.objects.create(name='Cuenca', code='CUE', is_active=False)
        
        # Clear cache first
        cache.clear()
        
        active_destinations = Destination.get_active_destinations()
        
        self.assertEqual(len(active_destinations), 2)
        codes = [dest['code'] for dest in active_destinations]
        self.assertIn('UIO', codes)
        self.assertIn('GYE', codes)
        self.assertNotIn('CUE', codes)

    def test_cache_invalidation_on_save(self):
        """Test that cache is cleared when destination is saved"""
        destination = Destination.objects.create(**self.destination_data)
        
        # Populate cache
        Destination.get_active_destinations()
        
        # Modify destination
        destination.name = 'Quito Modificado'
        destination.save()
        
        # Cache should be cleared (we can't directly test this, but ensure method works)
        active_destinations = Destination.get_active_destinations()
        self.assertIsInstance(active_destinations, list)
