from django.utils import timezone
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .models import Flight, Booking, Passenger

class BookingService:
    def __init__(self, user, flight):
        self.user = user
        self.flight = flight
        
    def validate_availability(self, passengers_count):
        """Validate if the flight is available for booking"""
        if self.flight.status not in ['SCHEDULED', 'CONFIRMED']:
            raise ValidationError(_('Este vuelo no está disponible para reservas.'))
            
        if self.flight.available_seats < passengers_count:
            raise ValidationError(_('No hay suficientes asientos disponibles.'))
            
        return True
        
    def validate_seats(self, selected_seats, passengers_count):
        """Validate selected seats"""
        if not selected_seats or len(selected_seats.split(',')) != passengers_count:
            raise ValidationError(_('Por favor, selecciona los asientos correctamente.'))
            
        # Aquí podrías agregar más validaciones específicas de asientos
        return True
        
    def validate_payment(self, payment_data):
        """Validate payment information"""
        required_fields = ['payment_method', 'card_number', 'card_name', 'card_expiry', 'card_cvv']
        
        if not all(payment_data.get(field) for field in required_fields):
            raise ValidationError(_('Por favor, complete toda la información de pago.'))
            
        # Validación básica de tarjeta
        card_number = payment_data['card_number'].replace(' ', '')
        if len(card_number) < 13 or len(payment_data['card_cvv']) < 3:
            raise ValidationError(_('Por favor, ingrese una tarjeta válida.'))
            
        return True
        
    @transaction.atomic
    def create_booking(self, booking_data):
        """Create a new booking with passenger information"""
        try:
            # Validate flight availability
            self.validate_availability(len(booking_data['passengers']))
            
            # Calculate total price
            total_price = self.flight.price * len(booking_data['passengers'])
            
            # Create booking record
            booking = Booking.objects.create(
                user=self.user,
                flight=self.flight,
                status=Booking.Status.CONFIRMED,
                passengers=len(booking_data['passengers']),
                total_price=total_price,
                special_requests=booking_data.get('special_requests', ''),
                payment_status=True,
                payment_date=timezone.now()
            )
            
            # Create passenger records
            seats = booking_data['selected_seats'].split(',')
            for i, passenger in enumerate(booking_data['passengers']):
                Passenger.objects.create(
                    booking=booking,
                    first_name=passenger['first_name'],
                    last_name=passenger['last_name'],
                    document_type=passenger['document_type'],
                    document_number=passenger['document_number'],
                    birth_date=passenger['birth_date'],
                    nationality=passenger['nationality'],
                    seat_number=seats[i] if i < len(seats) else ''
                )
            
            # Update flight available seats
            self.flight.available_seats -= len(booking_data['passengers'])
            self.flight.save()
            
            return booking
            
        except Exception as e:
            # En caso de error, el @transaction.atomic se encargará de hacer rollback
            raise ValidationError(str(e))

class BookingState:
    """Class to manage booking state in session"""
    def __init__(self, session):
        self.session = session
        
    @property
    def passengers_count(self):
        return self.session.get('booking_passengers')
        
    @passengers_count.setter
    def passengers_count(self, value):
        self.session['booking_passengers'] = value
        
    @property
    def selected_seats(self):
        return self.session.get('booking_selected_seats')
        
    @selected_seats.setter
    def selected_seats(self, value):
        self.session['booking_selected_seats'] = value
        
    @property
    def passenger_data(self):
        return self.session.get('booking_passenger_data', [])
        
    @passenger_data.setter
    def passenger_data(self, value):
        self.session['booking_passenger_data'] = value
        
    def clear(self):
        """Clear all booking related session data"""
        keys = ['booking_passengers', 'booking_selected_seats', 'booking_passenger_data']
        for key in keys:
            if key in self.session:
                del self.session[key] 