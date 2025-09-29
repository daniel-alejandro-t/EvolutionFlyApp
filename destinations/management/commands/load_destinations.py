from django.core.management.base import BaseCommand
from destinations.models import Destination

class Command(BaseCommand):
    help = 'Load initial destinations (cities of Ecuador)'

    def handle(self, *args, **options):
        destinations_data = [
            {'name': 'Quito', 'code': 'UIO', 'description': 'Capital del Ecuador, Patrimonio de la Humanidad'},
            {'name': 'Guayaquil', 'code': 'GYE', 'description': 'Puerto Principal del Ecuador'},
            {'name': 'Cuenca', 'code': 'CUE', 'description': 'Ciudad colonial, Patrimonio de la Humanidad'},
            {'name': 'Manta', 'code': 'MEC', 'description': 'Puerto de Manabí'},
            {'name': 'Loja', 'code': 'LOH', 'description': 'Puerta de entrada a la región amazónica'},
            {'name': 'Esmeraldas', 'code': 'ESM', 'description': 'Provincia Verde del Ecuador'},
            {'name': 'Machala', 'code': 'MCH', 'description': 'Capital bananera del mundo'},
            {'name': 'Ambato', 'code': 'ATF', 'description': 'Tierra de las flores y las frutas'},
            {'name': 'Riobamba', 'code': 'RBA', 'description': 'Sultana de los Andes'},
            {'name': 'Ibarra', 'code': 'IBR', 'description': 'Ciudad Blanca'},
            {'name': 'Baños', 'code': 'BAÑ', 'description': 'Puerta de entrada al Oriente'},
            {'name': 'Salinas', 'code': 'SLN', 'description': 'Balneario de la Península de Santa Elena'},
            {'name': 'Coca', 'code': 'OCC', 'description': 'Puerta de entrada al Yasuní'},
            {'name': 'Galápagos', 'code': 'GPS', 'description': 'Islas encantadas, laboratorio viviente de la evolución'},
        ]

        created_count = 0
        updated_count = 0

        for dest_data in destinations_data:
            destination, created = Destination.objects.get_or_create(
                code=dest_data['code'],
                defaults=dest_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created destination: {destination.name} ({destination.code})')
                )
            else:
                # Update existing destination
                destination.name = dest_data['name']
                destination.description = dest_data['description']
                destination.is_active = True
                destination.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'⚠ Updated destination: {destination.name} ({destination.code})')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Successfully processed {len(destinations_data)} destinations:'
                f'\n   • {created_count} created'
                f'\n   • {updated_count} updated'
            )
        )