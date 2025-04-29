from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import random
import string
from datetime import timedelta
from django.utils import timezone

class Destination(models.Model):
    name = models.CharField(_('nombre'), max_length=100)
    city = models.CharField(_('ciudad'), max_length=100)
    country = models.CharField(_('país'), max_length=100)
    description = models.TextField(_('descripción'), blank=True)
    image = models.ImageField(_('imagen'), upload_to='destinations/', blank=True, null=True)
    is_active = models.BooleanField(_('activo'), default=True)
    created_at = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    updated_at = models.DateTimeField(_('fecha de actualización'), auto_now=True)

    class Meta:
        verbose_name = _('Destino')
        verbose_name_plural = _('Destinos')
        ordering = ['name']

    def __str__(self):
        return f"{self.name}, {self.city}, {self.country}"

class AircraftType(models.Model):
    class Category(models.TextChoices):
        JET = 'JET', _('Jet Privado')
        LUXURY = 'LUXURY', _('Avión de Lujo')
        HELICOPTER = 'HELICOPTER', _('Helicóptero')

    name = models.CharField(_('nombre'), max_length=100)
    category = models.CharField(_('categoría'), max_length=20, choices=Category.choices)
    description = models.TextField(_('descripción'), blank=True)
    capacity = models.PositiveSmallIntegerField(_('capacidad'), validators=[MinValueValidator(1), MaxValueValidator(20)])
    image = models.ImageField(_('imagen'), upload_to='aircraft/', blank=True, null=True)
    amenities = models.JSONField(_('amenidades'), default=list, blank=True)
    is_active = models.BooleanField(_('activo'), default=True)
    created_at = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    updated_at = models.DateTimeField(_('fecha de actualización'), auto_now=True)

    class Meta:
        verbose_name = _('Tipo de Aeronave')
        verbose_name_plural = _('Tipos de Aeronaves')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

class Aircraft(models.Model):
    aircraft_type = models.ForeignKey(AircraftType, on_delete=models.PROTECT, related_name='aircraft')
    registration = models.CharField(_('registro'), max_length=20, unique=True)
    is_available = models.BooleanField(_('disponible'), default=True)
    maintenance_notes = models.TextField(_('notas de mantenimiento'), blank=True)
    last_maintenance = models.DateField(_('último mantenimiento'), null=True, blank=True)
    next_maintenance = models.DateField(_('próximo mantenimiento'), null=True, blank=True)
    created_at = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    updated_at = models.DateTimeField(_('fecha de actualización'), auto_now=True)

    class Meta:
        verbose_name = _('Aeronave')
        verbose_name_plural = _('Aeronaves')
        ordering = ['aircraft_type', 'registration']

    def __str__(self):
        return f"{self.aircraft_type.name} - {self.registration}"

class Flight(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', _('Programado')
        CONFIRMED = 'CONFIRMED', _('Confirmado')
        IN_PROGRESS = 'IN_PROGRESS', _('En Progreso')
        COMPLETED = 'COMPLETED', _('Completado')
        CANCELLED = 'CANCELLED', _('Cancelado')

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    aircraft = models.ForeignKey(Aircraft, on_delete=models.PROTECT, related_name='flights')
    origin = models.ForeignKey(Destination, on_delete=models.PROTECT, related_name='departures')
    destination = models.ForeignKey(Destination, on_delete=models.PROTECT, related_name='arrivals')
    departure_time = models.DateTimeField(_('hora de salida'))
    arrival_time = models.DateTimeField(_('hora de llegada'))
    price = models.DecimalField(_('precio'), max_digits=12, decimal_places=2)
    status = models.CharField(_('estado'), max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    max_passengers = models.PositiveSmallIntegerField(_('máximo de pasajeros'), validators=[MinValueValidator(1), MaxValueValidator(20)])
    available_seats = models.PositiveSmallIntegerField(_('asientos disponibles'), validators=[MinValueValidator(0), MaxValueValidator(20)])
    special_services = models.JSONField(_('servicios especiales'), default=list, blank=True)
    notes = models.TextField(_('notas'), blank=True)
    created_at = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    updated_at = models.DateTimeField(_('fecha de actualización'), auto_now=True)

    class Meta:
        verbose_name = _('Vuelo')
        verbose_name_plural = _('Vuelos')
        ordering = ['-departure_time']

    def __str__(self):
        return f"{self.origin} → {self.destination} - {self.departure_time.strftime('%d/%m/%Y %H:%M')}"

    def save(self, *args, **kwargs):
        if not self.available_seats:
            self.available_seats = self.max_passengers
        super().save(*args, **kwargs)

class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pendiente')
        CONFIRMED = 'CONFIRMED', _('Confirmada')
        CANCELLED = 'CANCELLED', _('Cancelada')
        COMPLETED = 'COMPLETED', _('Completada')

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='bookings')
    flight = models.ForeignKey(Flight, on_delete=models.PROTECT, related_name='bookings')
    status = models.CharField(_('estado'), max_length=20, choices=Status.choices, default=Status.PENDING)
    passengers = models.PositiveSmallIntegerField(_('pasajeros'), validators=[MinValueValidator(1), MaxValueValidator(20)])
    total_price = models.DecimalField(_('precio total'), max_digits=12, decimal_places=2)
    special_requests = models.TextField(_('solicitudes especiales'), blank=True)
    payment_status = models.BooleanField(_('pago realizado'), default=False)
    payment_date = models.DateTimeField(_('fecha de pago'), null=True, blank=True)
    created_at = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    updated_at = models.DateTimeField(_('fecha de actualización'), auto_now=True)
    booking_reference = models.CharField(_('referencia de reserva'), max_length=10, blank=True)

    class Meta:
        verbose_name = _('Reserva')
        verbose_name_plural = _('Reservas')
        ordering = ['-created_at']

    def __str__(self):
        return f"Reserva {self.uuid} - {self.user.email} - {self.flight}"

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.flight.price * self.passengers
        
        if not self.booking_reference:
            # Generate a random alphanumeric booking reference
            self.booking_reference = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        super().save(*args, **kwargs)
    
    def is_check_in_available(self):
        """Check if check-in is available for this booking"""
        if self.status != 'CONFIRMED' or not self.payment_status:
            return False
        
        # Check-in opens 48 hours before departure
        check_in_open_time = self.flight.departure_time - timedelta(hours=48)
        return timezone.now() >= check_in_open_time and timezone.now() <= self.flight.departure_time
    
    def has_checked_in(self):
        """Check if at least one passenger has completed check-in"""
        return self.passengers_info.filter(checked_in=True).exists()
    
    def all_checked_in(self):
        """Check if all passengers have completed check-in"""
        return self.passengers_info.filter(checked_in=True).count() == self.passengers

class Passenger(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='passengers_info')
    first_name = models.CharField(_('nombre'), max_length=100)
    last_name = models.CharField(_('apellido'), max_length=100)
    document_type = models.CharField(_('tipo de documento'), max_length=20, choices=[
        ('DNI', 'DNI'),
        ('PASSPORT', 'Pasaporte'),
        ('OTHER', 'Otro')
    ])
    document_number = models.CharField(_('número de documento'), max_length=30)
    birth_date = models.DateField(_('fecha de nacimiento'), null=True, blank=True)
    nationality = models.CharField(_('nacionalidad'), max_length=50)
    seat_number = models.CharField(_('número de asiento'), max_length=10, blank=True)
    checked_in = models.BooleanField(_('check-in realizado'), default=False)
    boarding_pass_issued = models.BooleanField(_('tarjeta de embarque emitida'), default=False)
    created_at = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    updated_at = models.DateTimeField(_('fecha de actualización'), auto_now=True)

    class Meta:
        verbose_name = _('Pasajero')
        verbose_name_plural = _('Pasajeros')
        ordering = ['booking', 'last_name', 'first_name']
        unique_together = [['booking', 'document_number']]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def check_in(self):
        """Mark passenger as checked in"""
        if not self.checked_in:
            self.checked_in = True
            if not self.seat_number:
                # Generate a random seat number if not assigned
                self.seat_number = f"{random.choice('ABCDEF')}{random.randint(1, 30)}"
            self.save()
        return self.checked_in

class CheckIn(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='check_in')
    completed = models.BooleanField(_('completado'), default=False)
    check_in_time = models.DateTimeField(_('hora de check-in'), null=True, blank=True)
    created_at = models.DateTimeField(_('fecha de creación'), auto_now_add=True)
    updated_at = models.DateTimeField(_('fecha de actualización'), auto_now=True)

    class Meta:
        verbose_name = _('Check-in')
        verbose_name_plural = _('Check-ins')
        ordering = ['-created_at']

    def __str__(self):
        return f"Check-in {self.booking.booking_reference}"
    
    def complete(self):
        """Complete the check-in process"""
        self.completed = True
        self.check_in_time = timezone.now()
        self.save()
        return self.completed