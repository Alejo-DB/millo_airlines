import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from flights.models import Destination, AircraftType, Aircraft, Flight

class Command(BaseCommand):
    help = 'Add test flights to the database'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Adding test flights...'))

        # Get active origins, destinations and aircraft
        origins = Destination.objects.filter(is_active=True, is_origin=True)
        destinations = Destination.objects.filter(is_active=True, is_origin=False)
        aircraft = Aircraft.objects.filter(is_available=True)

        if not origins.exists():
            self.stdout.write(self.style.ERROR('No active origins found. Please add origins first.'))
            return
        
        if not destinations.exists():
            self.stdout.write(self.style.ERROR('No active destinations found. Please add destinations first.'))
            return
        
        if not aircraft.exists():
            self.stdout.write(self.style.ERROR('No available aircraft found. Please add aircraft first.'))
            return

        # Create flights for the next 30 days
        with transaction.atomic():
            # Add flights between each origin and destination
            for origin in origins:
                for destination in destinations:
                    if origin.id != destination.id:  # Avoid same origin-destination
                        self.create_flights(origin, destination, aircraft)
            
            # Add specific flights for testing (April 27, 2025 - A Sunday)
            # This is useful for testing specific scenarios
            target_date = datetime(2025, 4, 27)
            el_dorado = Destination.objects.filter(id=7).first()
            dest_7 = Destination.objects.filter(id=8).first()
            
            if el_dorado and dest_7:
                self.create_specific_flights(el_dorado, dest_7, aircraft, target_date)
            
        self.stdout.write(self.style.SUCCESS('Successfully added test flights!'))

    def create_flights(self, origin, destination, aircraft_queryset):
        """Create flights between origin and destination for the next 30 days"""
        
        # Get number of flights per day (1-3)
        flights_per_day = random.randint(1, 3)
        
        # Generate flights for next 30 days
        for day in range(30):
            flight_date = timezone.now().date() + timedelta(days=day)
            
            for _ in range(flights_per_day):
                # Randomly choose aircraft and flight duration
                aircraft = random.choice(aircraft_queryset)
                flight_duration = random.randint(1, 8)  # 1-8 hours
                
                # Calculate departure and arrival times
                departure_hour = random.randint(6, 20)  # Between 6 AM and 8 PM
                departure_time = timezone.make_aware(
                    datetime.combine(flight_date, datetime.min.time()) + 
                    timedelta(hours=departure_hour)
                )
                arrival_time = departure_time + timedelta(hours=flight_duration)
                
                # Calculate price based on duration and aircraft type
                base_price = flight_duration * 500  # $500 per hour
                if aircraft.aircraft_type.category == 'HELICOPTER':
                    base_price *= 1.5  # Helicopters are more expensive
                elif aircraft.aircraft_type.category == 'JET':
                    base_price *= 2  # Jets are the most expensive
                
                # Add some randomness to the price
                price = base_price * random.uniform(0.9, 1.1)
                
                # Create the flight
                Flight.objects.create(
                    flight_number=f"ML{random.randint(1000, 9999)}",
                    origin=origin,
                    destination=destination,
                    departure_time=departure_time,
                    arrival_time=arrival_time,
                    aircraft=aircraft,
                    price=int(price),
                    max_passengers=aircraft.aircraft_type.capacity,
                    available_seats=aircraft.aircraft_type.capacity,
                    status='SCHEDULED'
                )

    def create_specific_flights(self, origin, destination, aircraft_queryset, target_date):
        """Create specific flights for testing purposes"""
        # Morning flight (8 AM)
        morning_departure = timezone.make_aware(
            datetime.combine(target_date.date(), datetime.min.time()) + 
            timedelta(hours=8)
        )
        morning_arrival = morning_departure + timedelta(hours=2)
        
        # Afternoon flight (2 PM)
        afternoon_departure = timezone.make_aware(
            datetime.combine(target_date.date(), datetime.min.time()) + 
            timedelta(hours=14)
        )
        afternoon_arrival = afternoon_departure + timedelta(hours=2)
        
        # Evening flight (7 PM)
        evening_departure = timezone.make_aware(
            datetime.combine(target_date.date(), datetime.min.time()) + 
            timedelta(hours=19)
        )
        evening_arrival = evening_departure + timedelta(hours=2)
        
        # Create the flights with different aircraft
        aircraft = list(aircraft_queryset)
        
        if len(aircraft) >= 3:
            # Morning flight - Economy
            Flight.objects.create(
                flight_number=f"ML{random.randint(1000, 9999)}",
                origin=origin,
                destination=destination,
                departure_time=morning_departure,
                arrival_time=morning_arrival,
                aircraft=aircraft[0],
                price=1200,
                max_passengers=aircraft[0].aircraft_type.capacity,
                available_seats=aircraft[0].aircraft_type.capacity,
                status='SCHEDULED'
            )
            
            # Afternoon flight - Business
            Flight.objects.create(
                flight_number=f"ML{random.randint(1000, 9999)}",
                origin=origin,
                destination=destination,
                departure_time=afternoon_departure,
                arrival_time=afternoon_arrival,
                aircraft=aircraft[1],
                price=2500,
                max_passengers=aircraft[1].aircraft_type.capacity,
                available_seats=aircraft[1].aircraft_type.capacity,
                status='SCHEDULED'
            )
            
            # Evening flight - First Class
            Flight.objects.create(
                flight_number=f"ML{random.randint(1000, 9999)}",
                origin=origin,
                destination=destination,
                departure_time=evening_departure,
                arrival_time=evening_arrival,
                aircraft=aircraft[2],
                price=5000,
                max_passengers=aircraft[2].aircraft_type.capacity,
                available_seats=aircraft[2].aircraft_type.capacity,
                status='SCHEDULED'
            ) 