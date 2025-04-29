from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Destination, AircraftType, Aircraft, Flight, Booking

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'is_active')
    list_filter = ('is_active', 'country')
    search_fields = ('name', 'city', 'country')
    ordering = ('name',)

@admin.register(AircraftType)
class AircraftTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'capacity', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = ('aircraft_type', 'registration', 'is_available', 'last_maintenance', 'next_maintenance')
    list_filter = ('is_available', 'aircraft_type')
    search_fields = ('registration', 'aircraft_type__name')
    ordering = ('aircraft_type', 'registration')

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('origin', 'destination', 'departure_time', 'arrival_time', 'price', 'status', 'available_seats')
    list_filter = ('status', 'origin', 'destination', 'departure_time')
    search_fields = ('origin__name', 'destination__name', 'aircraft__registration')
    ordering = ('-departure_time',)
    date_hierarchy = 'departure_time'
    readonly_fields = ('uuid', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('uuid', 'aircraft', 'origin', 'destination')
        }),
        (_('Horarios'), {
            'fields': ('departure_time', 'arrival_time')
        }),
        (_('Detalles'), {
            'fields': ('price', 'status', 'max_passengers', 'available_seats', 'special_services', 'notes')
        }),
        (_('Metadatos'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'user', 'flight', 'status', 'passengers', 'total_price', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('uuid', 'user__email', 'flight__uuid')
    ordering = ('-created_at',)
    readonly_fields = ('uuid', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('uuid', 'user', 'flight')
        }),
        (_('Detalles de la Reserva'), {
            'fields': ('status', 'passengers', 'total_price', 'special_requests')
        }),
        (_('Pago'), {
            'fields': ('payment_status', 'payment_date')
        }),
        (_('Metadatos'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
