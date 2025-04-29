from django.urls import path
from . import views

app_name = 'flights'

urlpatterns = [
    # Páginas principales
    path('', views.home, name='home'),
    path('search/', views.flight_search, name='flight_search'),
    
    # Vuelos
    path('flight/<int:pk>/', views.FlightDetailView.as_view(), name='flight_detail'),
    
    # Reservas
    path('flight/<int:pk>/book/', views.book_flight, name='book_flight'),
    path('booking/<uuid:uuid>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('booking/<uuid:uuid>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('booking/<uuid:uuid>/check-in/', views.start_check_in, name='start_check_in'),
    path('booking/<uuid:uuid>/check-in/confirm/', views.confirm_check_in, name='confirm_check_in'),
    path('booking/<uuid:uuid>/boarding-passes/', views.boarding_passes, name='boarding_passes'),
    path('booking/<uuid:uuid>/passenger/<int:passenger_id>/boarding-pass/', views.download_boarding_pass, name='download_boarding_pass'),
    path('booking/<uuid:uuid>/receipt/', views.download_receipt, name='download_receipt'),
    
    # Nueva experiencia de reserva
    path('flight/<int:flight_id>/booking/step/<int:step>/', views.booking_process, name='booking_process'),
    path('flight/<int:flight_id>/booking/confirm/', views.booking_confirm, name='booking_confirm'),
    
    # Panel de usuario
    path('dashboard/', views.UserDashboardView.as_view(), name='user_dashboard'),
    path('preferences/', views.update_preferences, name='update_preferences'),
    
    # Panel de administración
    path('flights-admin/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    
    # Admin URLs - Grouped under flights-admin prefix
    path('flights-admin/flights/', views.admin_flight_list, name='admin_flight_list'),
    path('flights-admin/flights/create/', views.admin_flight_create, name='admin_flight_create'),
    path('flights-admin/flights/<int:flight_id>/edit/', views.admin_flight_edit, name='admin_flight_edit'),
    path('flights-admin/flights/<int:flight_id>/delete/', views.admin_flight_delete, name='admin_flight_delete'),
    
    # Destination management
    path('flights-admin/destinations/', views.manage_destinations, name='manage_destinations'),
    path('flights-admin/destinations/create/', views.destination_create, name='destination_create'),
    path('flights-admin/destinations/<int:destination_id>/edit/', views.destination_edit, name='destination_edit'),
    path('flights-admin/destinations/<int:destination_id>/delete/', views.destination_delete, name='destination_delete'),
    
    # Aircraft management
    path('flights-admin/aircraft/', views.manage_aircraft, name='manage_aircraft'),
    path('flights-admin/aircraft/create/', views.aircraft_create, name='aircraft_create'),
    path('flights-admin/aircraft/<int:aircraft_id>/edit/', views.aircraft_edit, name='aircraft_edit'),
    path('flights-admin/aircraft/<int:aircraft_id>/delete/', views.aircraft_delete, name='aircraft_delete'),
    
    # Reports
    path('flights-admin/reports/', views.view_reports, name='view_reports'),
] 