import os
import django
import datetime
import random
from decimal import Decimal

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'millo_airlines.settings')
django.setup()

# Importar modelos después de configurar Django
from flights.models import Destination, AircraftType, Aircraft, Flight

def create_destinations():
    """Crear destinos comunes para pruebas"""
    destinations = [
        {
            'name': 'Aeropuerto El Dorado',
            'city': 'Bogotá',
            'country': 'Colombia',
            'description': 'Principal aeropuerto de Colombia, con múltiples destinos internacionales y nacionales.'
        },
        {
            'name': 'Aeropuerto Internacional Jorge Chávez',
            'city': 'Lima',
            'country': 'Perú',
            'description': 'El aeropuerto más importante de Perú, conecta con destinos en América y Europa.'
        },
        {
            'name': 'Aeropuerto Internacional Ministro Pistarini',
            'city': 'Buenos Aires',
            'country': 'Argentina',
            'description': 'Conocido como Ezeiza, es el principal aeropuerto de Argentina.'
        },
        {
            'name': 'Aeropuerto Internacional de Miami',
            'city': 'Miami',
            'country': 'Estados Unidos',
            'description': 'Uno de los aeropuertos más transitados de Estados Unidos, especialmente para conexiones con Latinoamérica.'
        },
        {
            'name': 'Aeropuerto Internacional de Madrid-Barajas',
            'city': 'Madrid',
            'country': 'España',
            'description': 'El aeropuerto más grande de España, hub principal para vuelos entre Europa y Latinoamérica.'
        },
        {
            'name': 'Aeropuerto Internacional de Cancún',
            'city': 'Cancún',
            'country': 'México',
            'description': 'Principal puerta de entrada a la Riviera Maya, destino turístico de clase mundial.'
        },
        {
            'name': 'Aeropuerto Internacional Comodoro Arturo Merino Benítez',
            'city': 'Santiago',
            'country': 'Chile',
            'description': 'El aeropuerto más importante de Chile, con múltiples conexiones internacionales.'
        },
        {
            'name': 'Aeropuerto Internacional José Martí',
            'city': 'La Habana',
            'country': 'Cuba',
            'description': 'El aeropuerto más grande de Cuba, principal punto de entrada para turistas internacionales.'
        }
    ]
    
    created_destinations = []
    for dest_data in destinations:
        destination, created = Destination.objects.get_or_create(
            name=dest_data['name'],
            city=dest_data['city'],
            country=dest_data['country'],
            defaults={
                'description': dest_data['description'],
                'is_active': True
            }
        )
        created_destinations.append(destination)
        if created:
            print(f"Creado destino: {destination}")
        else:
            print(f"Ya existe destino: {destination}")
    
    return created_destinations

def create_aircraft_types():
    """Crear tipos de aeronaves para pruebas"""
    aircraft_types = [
        {
            'name': 'Gulfstream G650',
            'category': AircraftType.Category.JET,
            'capacity': 19,
            'description': 'Jet privado de ultra largo alcance, perfecto para vuelos intercontinentales con el máximo lujo.',
            'amenities': ['Wi-Fi de alta velocidad', 'Bar completo', 'Asientos de cuero', 'Camas', 'Cocina gourmet']
        },
        {
            'name': 'Bombardier Global 7500',
            'category': AircraftType.Category.JET,
            'capacity': 17,
            'description': 'El jet de negocios más grande y de mayor alcance del mundo, con cuatro zonas de cabina distintas.',
            'amenities': ['Entretenimiento 4K', 'Cocina completa', 'Suite principal', 'Oficina privada', 'Ducha']
        },
        {
            'name': 'Embraer Phenom 300E',
            'category': AircraftType.Category.JET,
            'capacity': 10,
            'description': 'Jet ligero con rendimiento excepcional y cabina lujosa, ideal para vuelos regionales.',
            'amenities': ['Wi-Fi', 'Asientos de cuero', 'Baño privado', 'Catering premium']
        },
        {
            'name': 'Airbus ACJ320neo',
            'category': AircraftType.Category.LUXURY,
            'capacity': 19,
            'description': 'Versión VIP del Airbus A320, ofrece espacio amplio y capacidades de largo alcance.',
            'amenities': ['Sala de conferencias', 'Dormitorios privados', 'Lounge', 'Entretenimiento de última generación']
        },
        {
            'name': 'Boeing BBJ 737',
            'category': AircraftType.Category.LUXURY,
            'capacity': 20,
            'description': 'Business Jet basado en el 737, con interiores personalizados y lujo extremo.',
            'amenities': ['Sala de juntas', 'Dormitorio principal', 'Baño con ducha', 'Oficina', 'Sala de estar']
        },
        {
            'name': 'Bell 525 Relentless',
            'category': AircraftType.Category.HELICOPTER,
            'capacity': 16,
            'description': 'Helicóptero comercial de lujo con aviónica avanzada y máximo confort.',
            'amenities': ['Cabina silenciosa', 'Asientos VIP', 'Aire acondicionado', 'Iluminación personalizada']
        },
        {
            'name': 'AgustaWestland AW139',
            'category': AircraftType.Category.HELICOPTER,
            'capacity': 15,
            'description': 'Helicóptero ejecutivo de medio tamaño con configuración VIP.',
            'amenities': ['Interior personalizable', 'Aislamiento acústico', 'Sistemas de entretenimiento', 'Comunicaciones satelitales']
        }
    ]
    
    created_types = []
    for type_data in aircraft_types:
        aircraft_type, created = AircraftType.objects.get_or_create(
            name=type_data['name'],
            defaults={
                'category': type_data['category'],
                'capacity': type_data['capacity'],
                'description': type_data['description'],
                'amenities': type_data['amenities'],
                'is_active': True
            }
        )
        created_types.append(aircraft_type)
        if created:
            print(f"Creado tipo de aeronave: {aircraft_type}")
        else:
            print(f"Ya existe tipo de aeronave: {aircraft_type}")
    
    return created_types

def create_aircraft(aircraft_types):
    """Crear aeronaves basadas en los tipos disponibles"""
    aircraft_data = [
        {'type': 'Gulfstream G650', 'registration': 'HK-5001'},
        {'type': 'Gulfstream G650', 'registration': 'HK-5002'},
        {'type': 'Bombardier Global 7500', 'registration': 'HK-5003'},
        {'type': 'Bombardier Global 7500', 'registration': 'HK-5004'},
        {'type': 'Embraer Phenom 300E', 'registration': 'HK-5005'},
        {'type': 'Embraer Phenom 300E', 'registration': 'HK-5006'},
        {'type': 'Airbus ACJ320neo', 'registration': 'HK-5007'},
        {'type': 'Boeing BBJ 737', 'registration': 'HK-5008'},
        {'type': 'Bell 525 Relentless', 'registration': 'HK-5009'},
        {'type': 'AgustaWestland AW139', 'registration': 'HK-5010'},
    ]
    
    # Crear un diccionario para buscar tipos de aeronaves por nombre
    type_dict = {aircraft_type.name: aircraft_type for aircraft_type in aircraft_types}
    
    created_aircraft = []
    for aircraft_item in aircraft_data:
        aircraft_type = type_dict.get(aircraft_item['type'])
        if not aircraft_type:
            print(f"Tipo de aeronave no encontrado: {aircraft_item['type']}")
            continue
            
        aircraft, created = Aircraft.objects.get_or_create(
            registration=aircraft_item['registration'],
            defaults={
                'aircraft_type': aircraft_type,
                'is_available': True,
                'last_maintenance': datetime.date.today() - datetime.timedelta(days=30),
                'next_maintenance': datetime.date.today() + datetime.timedelta(days=60)
            }
        )
        created_aircraft.append(aircraft)
        if created:
            print(f"Creada aeronave: {aircraft}")
        else:
            print(f"Ya existe aeronave: {aircraft}")
    
    return created_aircraft

def create_flights(destinations, aircraft):
    """Crear vuelos entre los destinos con las aeronaves disponibles"""
    # Asegurarse de que tenemos al menos 2 destinos y 1 aeronave
    if len(destinations) < 2 or not aircraft:
        print("No hay suficientes destinos o aeronaves para crear vuelos")
        return []
    
    # Fechas para los próximos 30 días
    today = datetime.date.today()
    dates = [today + datetime.timedelta(days=i) for i in range(1, 31)]
    
    created_flights = []
    
    # Crear vuelos entre todas las combinaciones de destinos
    for i, origin in enumerate(destinations):
        for j, destination in enumerate(destinations):
            if i == j:  # No crear vuelos al mismo destino
                continue
            
            # Crear 2-3 vuelos aleatorios entre estos destinos
            num_flights = random.randint(2, 3)
            for _ in range(num_flights):
                # Elegir fecha aleatoria y hora de salida
                flight_date = random.choice(dates)
                hour = random.randint(6, 22)
                minute = random.choice([0, 15, 30, 45])
                departure_time = datetime.datetime.combine(
                    flight_date,
                    datetime.time(hour, minute),
                    tzinfo=datetime.timezone.utc
                )
                
                # Calcular hora de llegada (entre 1 y 10 horas después)
                flight_duration = datetime.timedelta(hours=random.randint(1, 10))
                arrival_time = departure_time + flight_duration
                
                # Elegir aeronave aleatoria
                aircraft_instance = random.choice(aircraft)
                
                # Calcular precio (entre $500 y $5000)
                price = Decimal(random.randint(500, 5000))
                
                # Configurar asientos disponibles
                max_passengers = min(aircraft_instance.aircraft_type.capacity, 20)
                available_seats = random.randint(0, max_passengers)
                
                # Crear el vuelo
                flight, created = Flight.objects.get_or_create(
                    origin=origin,
                    destination=destination,
                    departure_time=departure_time,
                    defaults={
                        'aircraft': aircraft_instance,
                        'arrival_time': arrival_time,
                        'price': price,
                        'status': Flight.Status.SCHEDULED,
                        'max_passengers': max_passengers,
                        'available_seats': available_seats,
                        'special_services': random.sample([
                            'Catering gourmet', 'Transfer terrestre', 'Concierge VIP', 
                            'Check-in privado', 'Servicio de equipaje premium'
                        ], k=random.randint(1, 3))
                    }
                )
                
                if created:
                    created_flights.append(flight)
                    print(f"Creado vuelo: {flight}")
                else:
                    print(f"Ya existe vuelo: {flight}")
    
    return created_flights

def main():
    print("Poblando base de datos con datos de prueba...")
    
    # Crear datos en orden de dependencia
    destinations = create_destinations()
    aircraft_types = create_aircraft_types()
    aircraft = create_aircraft(aircraft_types)
    flights = create_flights(destinations, aircraft)
    
    print(f"\nResumen de datos creados:")
    print(f"- Destinos: {len(destinations)}")
    print(f"- Tipos de aeronaves: {len(aircraft_types)}")
    print(f"- Aeronaves: {len(aircraft)}")
    print(f"- Vuelos: {len(flights)}")
    print("\nBase de datos poblada correctamente.")

if __name__ == "__main__":
    main() 