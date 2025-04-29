from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from flights.models import Destination, AircraftType, Aircraft
from datetime import date, timedelta
import os
import shutil
from django.conf import settings

class Command(BaseCommand):
    help = 'Adds test data (destinations and aircraft) to the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Adding test data to the database...'))
        
        # Add destinations
        self.add_destinations()
        
        # Add aircraft types
        self.add_aircraft_types()
        
        # Add aircraft
        self.add_aircraft()
        
        self.stdout.write(self.style.SUCCESS('Successfully added test data!'))
    
    def copy_image(self, source_path, destination_path):
        """Copy image from static to media directory."""
        source_full_path = os.path.join(settings.BASE_DIR, 'static', source_path)
        destination_full_path = os.path.join(settings.MEDIA_ROOT, destination_path)
        
        # Create destination directory if it doesn't exist
        os.makedirs(os.path.dirname(destination_full_path), exist_ok=True)
        
        # Copy the file if it exists
        if os.path.exists(source_full_path):
            shutil.copy2(source_full_path, destination_full_path)
            return True
        return False

    def add_destinations(self):
        self.stdout.write('Adding destinations...')
        
        destinations = [
            # Colombia
            {
                'name': 'Aeropuerto El Dorado',
                'city': 'Bogotá',
                'country': 'Colombia',
                'description': 'Principal aeropuerto de Colombia, hub internacional.',
                'is_active': True,
            },
            {
                'name': 'Aeropuerto Internacional Rafael Núñez',
                'city': 'Cartagena',
                'country': 'Colombia',
                'description': 'Aeropuerto que sirve a la ciudad turística de Cartagena.',
                'is_active': True,
            },
            {
                'name': 'Aeropuerto Internacional José María Córdova',
                'city': 'Medellín',
                'country': 'Colombia',
                'description': 'Principal aeropuerto que sirve a la ciudad de Medellín.',
                'is_active': True,
            },
            # International
            {
                'name': 'Aeropuerto Internacional de Miami',
                'city': 'Miami',
                'country': 'Estados Unidos',
                'description': 'Uno de los aeropuertos más transitados para viajes entre América Latina y Estados Unidos.',
                'is_active': True,
            },
            {
                'name': 'Aeropuerto Internacional Benito Juárez',
                'city': 'Ciudad de México',
                'country': 'México',
                'description': 'Principal aeropuerto de México y hub para América Latina.',
                'is_active': True,
            },
            {
                'name': 'Aeropuerto Internacional de Tocumen',
                'city': 'Panamá',
                'country': 'Panamá',
                'description': 'Hub importante que conecta América del Norte y del Sur.',
                'is_active': True,
            },
            {
                'name': 'Aeropuerto Internacional de Madrid Barajas',
                'city': 'Madrid',
                'country': 'España',
                'description': 'Principal aeropuerto de España y conexión con Europa.',
                'is_active': True,
            },
            {
                'name': 'Aeropuerto Internacional de París-Charles de Gaulle',
                'city': 'París',
                'country': 'Francia',
                'description': 'Uno de los aeropuertos más importantes de Europa.',
                'is_active': True,
            },
            {
                'name': 'Aeropuerto Internacional de Buenos Aires Ministro Pistarini',
                'city': 'Buenos Aires',
                'country': 'Argentina',
                'description': 'Principal aeropuerto de Argentina.',
                'is_active': True,
            },
            {
                'name': 'Aeropuerto Internacional de Santiago',
                'city': 'Santiago',
                'country': 'Chile',
                'description': 'Principal aeropuerto de Chile y puerta de entrada a la región.',
                'is_active': True,
            },
        ]
        
        for dest_data in destinations:
            destination, created = Destination.objects.get_or_create(
                name=dest_data['name'],
                defaults=dest_data
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Added destination: {destination.name}'))
            else:
                self.stdout.write(f'Destination already exists: {destination.name}')
    
    def add_aircraft_types(self):
        self.stdout.write('Adding aircraft types...')
        
        aircraft_types = [
            {
                'name': 'Boeing 737-800',
                'category': 'JET',
                'description': 'Avión de pasillo único, utilizado principalmente para rutas cortas y medianas.',
                'capacity': 160,
                'amenities': ['WiFi', 'Entertainment System', 'Power Outlets'],
                'is_active': True,
                'image_source': 'img/Qantas Boeing 737 800.G03.watermarked.2k.png',
                'image_dest': 'aircraft/Qantas Boeing 737 800.G03.watermarked.2k.png'
            },
            {
                'name': 'Airbus A320',
                'category': 'JET',
                'description': 'Aeronave de pasillo único, competidor directo del Boeing 737.',
                'capacity': 150,
                'amenities': ['WiFi', 'Entertainment System', 'USB Ports'],
                'is_active': True,
                'image_source': 'img/Airbus A320.G03.watermarked.2k.png',
                'image_dest': 'aircraft/Airbus A320.G03.watermarked.2k.png'
            },
            {
                'name': 'Boeing 787 Dreamliner',
                'category': 'LUXURY',
                'description': 'Avión de largo alcance con tecnología avanzada y mayor comodidad para pasajeros.',
                'capacity': 20,
                'amenities': ['WiFi', 'Premium Entertainment', 'Lie-flat Seats', 'Gourmet Meals', 'Premium Bar'],
                'is_active': True,
                'image_source': 'img/Boeing 787-8 Dreamliner.G11.watermarked.2k.png',
                'image_dest': 'aircraft/Boeing 787-8 Dreamliner.G11.watermarked.2k.png'
            },
            {
                'name': 'Airbus A350',
                'category': 'LUXURY',
                'description': 'Aeronave de fuselaje ancho para vuelos intercontinentales, con alta eficiencia de combustible.',
                'capacity': 18,
                'amenities': ['WiFi', 'Premium Entertainment', 'Lie-flat Seats', 'Gourmet Meals', 'Premium Bar'],
                'is_active': True,
                'image_source': 'img/Airbus ACJ320.G03.watermarked.2k.png',
                'image_dest': 'aircraft/Airbus ACJ320.G03.watermarked.2k.png'
            },
            {
                'name': 'Embraer E190',
                'category': 'JET',
                'description': 'Jet regional de tamaño medio, ideal para rutas con menos demanda.',
                'capacity': 15,
                'amenities': ['WiFi', 'Snack Service'],
                'is_active': True,
                'image_source': 'img/Embraer ERJ-190 Jet Blue.G11.watermarked.2k.png',
                'image_dest': 'aircraft/Embraer ERJ-190 Jet Blue.G11.watermarked.2k.png'
            },
        ]
        
        for type_data in aircraft_types:
            # Copy image file
            image_source = type_data.pop('image_source')
            image_dest = type_data.pop('image_dest')
            
            if self.copy_image(image_source, image_dest):
                type_data['image'] = image_dest
            
            aircraft_type, created = AircraftType.objects.get_or_create(
                name=type_data['name'],
                defaults=type_data
            )
            
            if not created:
                # Update existing record with new image
                if 'image' in type_data:
                    aircraft_type.image = type_data['image']
                    aircraft_type.save()
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Added aircraft type: {aircraft_type.name}'))
            else:
                self.stdout.write(f'Updated aircraft type: {aircraft_type.name}')
    
    def add_aircraft(self):
        self.stdout.write('Adding aircraft...')
        
        # Ensure we have aircraft types
        if not AircraftType.objects.exists():
            self.stdout.write(self.style.ERROR('No aircraft types found. Cannot add aircraft.'))
            return
        
        # Get aircraft types
        boeing_737 = AircraftType.objects.filter(name='Boeing 737-800').first()
        airbus_a320 = AircraftType.objects.filter(name='Airbus A320').first()
        boeing_787 = AircraftType.objects.filter(name='Boeing 787 Dreamliner').first()
        airbus_a350 = AircraftType.objects.filter(name='Airbus A350').first()
        embraer_e190 = AircraftType.objects.filter(name='Embraer E190').first()
        
        # Calculate dates for maintenance
        today = date.today()
        last_maintenance = today - timedelta(days=30)
        next_maintenance = today + timedelta(days=60)
        
        aircraft = [
            # Boeing 737s
            {
                'registration': 'MLA-B731', 
                'aircraft_type': boeing_737, 
                'is_available': True,
                'maintenance_notes': 'Mantenimiento rutinario completado',
                'last_maintenance': last_maintenance,
                'next_maintenance': next_maintenance
            },
            {
                'registration': 'MLA-B732', 
                'aircraft_type': boeing_737, 
                'is_available': True,
                'maintenance_notes': 'Mantenimiento rutinario completado',
                'last_maintenance': last_maintenance,
                'next_maintenance': next_maintenance
            },
            {
                'registration': 'MLA-B733', 
                'aircraft_type': boeing_737, 
                'is_available': True,
                'maintenance_notes': 'Mantenimiento rutinario completado',
                'last_maintenance': last_maintenance,
                'next_maintenance': next_maintenance
            },
            
            # Airbus A320s
            {
                'registration': 'MLA-A321', 
                'aircraft_type': airbus_a320, 
                'is_available': True,
                'maintenance_notes': 'Mantenimiento rutinario completado',
                'last_maintenance': last_maintenance,
                'next_maintenance': next_maintenance
            },
            {
                'registration': 'MLA-A322', 
                'aircraft_type': airbus_a320, 
                'is_available': True,
                'maintenance_notes': 'Mantenimiento rutinario completado',
                'last_maintenance': last_maintenance,
                'next_maintenance': next_maintenance
            },
            {
                'registration': 'MLA-A323', 
                'aircraft_type': airbus_a320, 
                'is_available': True,
                'maintenance_notes': 'Mantenimiento rutinario completado',
                'last_maintenance': last_maintenance,
                'next_maintenance': next_maintenance
            },
            
            # Boeing 787s
            {
                'registration': 'MLA-B781', 
                'aircraft_type': boeing_787, 
                'is_available': True,
                'maintenance_notes': 'Mantenimiento completo de lujo',
                'last_maintenance': last_maintenance,
                'next_maintenance': next_maintenance
            },
            {
                'registration': 'MLA-B782', 
                'aircraft_type': boeing_787, 
                'is_available': True,
                'maintenance_notes': 'Mantenimiento completo de lujo',
                'last_maintenance': last_maintenance,
                'next_maintenance': next_maintenance
            },
            
            # Airbus A350s
            {
                'registration': 'MLA-A351', 
                'aircraft_type': airbus_a350, 
                'is_available': True,
                'maintenance_notes': 'Mantenimiento completo de lujo',
                'last_maintenance': last_maintenance,
                'next_maintenance': next_maintenance
            },
            {
                'registration': 'MLA-A352', 
                'aircraft_type': airbus_a350, 
                'is_available': True,
                'maintenance_notes': 'Mantenimiento completo de lujo',
                'last_maintenance': last_maintenance,
                'next_maintenance': next_maintenance
            },
            
            # Embraer E190s
            {
                'registration': 'MLA-E191', 
                'aircraft_type': embraer_e190, 
                'is_available': True,
                'maintenance_notes': 'Mantenimiento standard completado',
                'last_maintenance': last_maintenance,
                'next_maintenance': next_maintenance
            },
            {
                'registration': 'MLA-E192', 
                'aircraft_type': embraer_e190, 
                'is_available': True,
                'maintenance_notes': 'Mantenimiento standard completado',
                'last_maintenance': last_maintenance,
                'next_maintenance': next_maintenance
            },
        ]
        
        for aircraft_data in aircraft:
            if not aircraft_data['aircraft_type']:
                self.stdout.write(self.style.WARNING(f'Skipping aircraft {aircraft_data["registration"]} due to missing aircraft type.'))
                continue
                
            aircraft_obj, created = Aircraft.objects.get_or_create(
                registration=aircraft_data['registration'],
                defaults=aircraft_data
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Added aircraft: {aircraft_obj.registration} ({aircraft_obj.aircraft_type.name})'))
            else:
                self.stdout.write(f'Aircraft already exists: {aircraft_obj.registration}') 