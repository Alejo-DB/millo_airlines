from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Booking, Flight

@receiver(pre_save, sender=Booking)
def update_flight_seats(sender, instance, **kwargs):
    """Actualizar asientos disponibles cuando se crea o actualiza una reserva"""
    if not instance.pk:  # Nueva reserva
        flight = instance.flight
        flight.available_seats -= instance.passengers
        flight.save()
    else:  # Actualización de reserva existente
        old_instance = Booking.objects.get(pk=instance.pk)
        if old_instance.passengers != instance.passengers:
            flight = instance.flight
            flight.available_seats += old_instance.passengers - instance.passengers
            flight.save()

@receiver(post_save, sender=Booking)
def send_booking_confirmation(sender, instance, created, **kwargs):
    """Enviar confirmación de reserva al usuario"""
    if created and instance.status == 'CONFIRMED':
        # Aquí se implementaría el envío de email de confirmación
        pass

@receiver(pre_save, sender=Flight)
def update_flight_status(sender, instance, **kwargs):
    """Actualizar estado del vuelo basado en la fecha"""
    now = timezone.now()
    
    if instance.departure_time <= now and instance.status == 'CONFIRMED':
        instance.status = 'IN_PROGRESS'
    elif instance.arrival_time <= now and instance.status == 'IN_PROGRESS':
        instance.status = 'COMPLETED' 