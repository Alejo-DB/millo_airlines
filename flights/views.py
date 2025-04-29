from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, TemplateView, FormView
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from datetime import datetime, timedelta
from .models import Flight, Booking, Destination, AircraftType, Aircraft, Passenger, CheckIn
from .forms import (
    FlightSearchForm, BookingForm, UserPreferencesForm, PassengerForm, FlightForm,
    FlightSelectionForm, SeatSelectionForm, PassengerFormSet, PaymentForm
)
from django.utils import timezone
from django.db import transaction
from io import BytesIO
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from .services import BookingService
from .enums import BookingState

User = get_user_model()

def home(request):
    """Vista para la página principal con búsqueda de vuelos"""
    destinations = Destination.objects.filter(is_active=True)[:6]
    aircraft_types = AircraftType.objects.filter(is_active=True)
    
    context = {
        'destinations': destinations,
        'aircraft_types': aircraft_types,
    }
    return render(request, 'flights/home.html', context)

def flight_search(request):
    """View for searching available flights"""
    form = FlightSearchForm(request.GET or None)
    flights = Flight.objects.none()
    search_performed = False
    
    if form.is_valid():
        search_performed = True
        origin = form.cleaned_data.get('origin')
        destination = form.cleaned_data.get('destination')
        departure_date = form.cleaned_data.get('departure_date')
        passengers = form.cleaned_data.get('passengers')
        
        # Convert date to timezone-aware datetime for comparison
        departure_start = timezone.make_aware(datetime.combine(departure_date, datetime.min.time()))
        departure_end = timezone.make_aware(datetime.combine(departure_date, datetime.max.time()))
        
        # Filtrar vuelos disponibles
        flights = Flight.objects.filter(
            origin=origin,
            destination=destination,
            departure_time__range=(departure_start, departure_end),
            available_seats__gte=passengers,
            status__in=['SCHEDULED', 'CONFIRMED']
        ).select_related(
            'origin',
            'destination',
            'aircraft',
            'aircraft__aircraft_type'
        ).order_by('departure_time')
        
        # Si no hay vuelos disponibles para la fecha seleccionada,
        # buscar vuelos alternativos en los próximos 3 días
        if not flights.exists():
            alternative_end = departure_start + timezone.timedelta(days=3)
            alternative_flights = Flight.objects.filter(
                origin=origin,
                destination=destination,
                departure_time__range=(departure_start, alternative_end),
                available_seats__gte=passengers,
                status__in=['SCHEDULED', 'CONFIRMED']
            ).select_related(
                'origin',
                'destination',
                'aircraft',
                'aircraft__aircraft_type'
            ).order_by('departure_time')
            
            if alternative_flights.exists():
                messages.info(
                    request,
                    _('No flights found for the selected date. Showing available flights for the next 3 days.')
                )
                flights = alternative_flights
    
    context = {
        'form': form,
        'flights': flights,
        'search_performed': search_performed,
        'search_params': {
            'origin': form.cleaned_data.get('origin').name if form.is_valid() and form.cleaned_data.get('origin') else None,
            'destination': form.cleaned_data.get('destination').name if form.is_valid() and form.cleaned_data.get('destination') else None,
            'departure_date': form.cleaned_data.get('departure_date') if form.is_valid() else None,
            'passengers': form.cleaned_data.get('passengers') if form.is_valid() else None,
        } if form.is_valid() else None
    }
    return render(request, 'flights/flight_search.html', context)

class FlightDetailView(DetailView):
    """Vista para ver detalles de un vuelo específico"""
    model = Flight
    template_name = 'flights/flight_detail.html'
    context_object_name = 'flight'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['booking_form'] = BookingForm(flight=self.object)
        return context

@login_required
def book_flight(request, pk):
    """Vista para reservar un vuelo"""
    flight = get_object_or_404(Flight, pk=pk)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, flight=flight)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.flight = flight
            booking.save()
            
            # Actualizar asientos disponibles
            flight.available_seats -= booking.passengers
            flight.save()
            
            messages.success(request, _('Reserva creada exitosamente'))
            return redirect('flights:booking_detail', uuid=booking.uuid)
    else:
        form = BookingForm(flight=flight)
    
    context = {
        'form': form,
        'flight': flight,
    }
    return render(request, 'flights/book_flight.html', context)

class BookingDetailView(LoginRequiredMixin, DetailView):
    """Vista para ver detalles de una reserva"""
    model = Booking
    template_name = 'flights/booking_detail.html'
    context_object_name = 'booking'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

class UserDashboardView(LoginRequiredMixin, ListView):
    """Vista para el panel de usuario"""
    model = Booking
    template_name = 'flights/user_dashboard.html'
    context_object_name = 'bookings'
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Obtener reservas activas
        context['active_bookings'] = self.get_queryset().filter(
            status__in=['PENDING', 'CONFIRMED']
        )
        
        # Obtener reservas pasadas
        context['past_bookings'] = self.get_queryset().filter(
            status__in=['COMPLETED', 'CANCELLED']
        )
        
        # Obtener destinos preferidos
        if user.preferred_destinations:
            context['preferred_destinations'] = Destination.objects.filter(
                id__in=user.preferred_destinations
            ).select_related()
        else:
            context['preferred_destinations'] = []
        
        return context

@login_required
def update_preferences(request):
    """Vista para actualizar preferencias de usuario"""
    destinations = Destination.objects.filter(is_active=True)
    
    if request.method == 'POST':
        form = UserPreferencesForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.preferred_destinations = [str(dest.id) for dest in form.cleaned_data['preferred_destinations']]
            user.save()
            messages.success(request, _('Preferences updated successfully'))
            return redirect('flights:user_dashboard')
    else:
        initial = {
            'preferred_destinations': Destination.objects.filter(id__in=request.user.preferred_destinations)
        }
        form = UserPreferencesForm(instance=request.user, initial=initial)
    
    context = {
        'form': form,
        'destinations': destinations,
    }
    return render(request, 'flights/update_preferences.html', context)

class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Vista para el panel de administración"""
    model = Flight
    template_name = 'flights/admin_dashboard.html'
    context_object_name = 'flights'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        return Flight.objects.all().order_by('-departure_time')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas para el panel
        context['total_flights'] = Flight.objects.count() or 0
        context['active_bookings'] = Booking.objects.filter(
            status__in=['PENDING', 'CONFIRMED'],
            flight__departure_time__gte=timezone.now()
        ).count() or 0
        context['total_users'] = User.objects.filter(user_type='CLIENT').count() or 0
        
        # Vuelos próximos - Mostrar solo vuelos futuros que no estén cancelados
        context['upcoming_flights'] = Flight.objects.filter(
            departure_time__gte=timezone.now(),
            status__in=['SCHEDULED', 'CONFIRMED']
        ).order_by('departure_time')
        
        # Reservas recientes - Solo mostrar reservas activas
        context['recent_bookings'] = Booking.objects.filter(
            status__in=['PENDING', 'CONFIRMED'],
            flight__departure_time__gte=timezone.now()
        ).order_by('-created_at')[:5]
        
        return context

@login_required
def cancel_booking(request, uuid):
    booking = get_object_or_404(Booking, uuid=uuid, user=request.user)
    
    # Only allow cancellation if status is pending or confirmed and the flight is not within 24 hours
    if booking.status in ['PENDING', 'CONFIRMED']:
        cancel_deadline = booking.flight.departure_time - timezone.timedelta(hours=24)
        if timezone.now() < cancel_deadline:
            try:
                with transaction.atomic():
                    # Update flight seat availability
                    booking.flight.available_seats += booking.passengers
                    booking.flight.save()
                    
                    # Mark booking as cancelled
                    booking.status = 'CANCELLED'
                    booking.save()
                    
                    messages.success(request, _('Reserva cancelada correctamente.'))
            except Exception as e:
                messages.error(request, _('Error al cancelar la reserva. Por favor, intente nuevamente.'))
        else:
            messages.error(request, _('No se puede cancelar una reserva dentro de las 24 horas previas al vuelo.'))
    else:
        messages.error(request, _('Esta reserva no puede ser cancelada.'))
    
    return redirect('flights:booking_detail', uuid=uuid)

@login_required
def start_check_in(request, uuid):
    """Initialize the check-in process for a booking"""
    booking = get_object_or_404(Booking, uuid=uuid, user=request.user)
    
    # Validate check-in availability
    if not booking.is_check_in_available():
        messages.error(request, _('El check-in no está disponible para esta reserva.'))
        return redirect('flights:booking_detail', uuid=uuid)
    
    # Create or get check-in record
    check_in, created = CheckIn.objects.get_or_create(booking=booking)
    
    if request.method == 'POST':
        # Handle form submissions for passenger information
        passenger_forms = []
        form_valid = True
        
        for i in range(booking.passengers):
            prefix = f"passenger_{i}"
            
            # Check if this passenger already exists
            passenger_id = request.POST.get(f"{prefix}-id", None)
            if passenger_id:
                passenger = get_object_or_404(Passenger, id=passenger_id, booking=booking)
                form = PassengerForm(request.POST, prefix=prefix, instance=passenger)
            else:
                form = PassengerForm(request.POST, prefix=prefix)
            
            if form.is_valid():
                passenger_forms.append(form)
            else:
                form_valid = False
                passenger_forms.append(form)
        
        if form_valid:
            for form in passenger_forms:
                passenger = form.save(commit=False)
                passenger.booking = booking
                passenger.save()
                
            messages.success(request, _('Información de pasajeros guardada correctamente.'))
            return redirect('flights:confirm_check_in', uuid=uuid)
    else:
        # Display passenger forms for check-in
        passenger_forms = []
        existing_passengers = booking.passengers_info.all()
        
        # Reuse existing passenger data or create new forms
        for i in range(booking.passengers):
            if i < existing_passengers.count():
                form = PassengerForm(prefix=f"passenger_{i}", instance=existing_passengers[i])
            else:
                form = PassengerForm(prefix=f"passenger_{i}")
            passenger_forms.append(form)
    
    return render(request, 'flights/check_in.html', {
        'booking': booking,
        'passenger_forms': passenger_forms,
        'check_in': check_in,
    })

@login_required
def confirm_check_in(request, uuid):
    """Confirm check-in and generate boarding passes"""
    booking = get_object_or_404(Booking, uuid=uuid, user=request.user)
    check_in = get_object_or_404(CheckIn, booking=booking)
    
    # Ensure all passengers have info registered
    if booking.passengers_info.count() < booking.passengers:
        messages.error(request, _('Debe completar la información de todos los pasajeros.'))
        return redirect('flights:start_check_in', uuid=uuid)
    
    if request.method == 'POST':
        # Process check-in confirmation
        with transaction.atomic():
            # Mark all passengers as checked in
            for passenger in booking.passengers_info.all():
                passenger.check_in()
            
            # Complete the check-in process
            check_in.complete()
            
            messages.success(request, _('Check-in completado correctamente. Puede descargar sus tarjetas de embarque.'))
            return redirect('flights:boarding_passes', uuid=uuid)
    
    return render(request, 'flights/confirm_check_in.html', {
        'booking': booking,
        'check_in': check_in,
        'passengers': booking.passengers_info.all(),
    })

@login_required
def boarding_passes(request, uuid):
    """View and download boarding passes"""
    booking = get_object_or_404(Booking, uuid=uuid, user=request.user)
    
    # Ensure check-in is completed
    if not hasattr(booking, 'check_in') or not booking.check_in.completed:
        messages.error(request, _('Debe completar el check-in primero.'))
        return redirect('flights:booking_detail', uuid=uuid)
    
    # Mark boarding passes as issued
    for passenger in booking.passengers_info.all():
        if not passenger.boarding_pass_issued:
            passenger.boarding_pass_issued = True
            passenger.save()
    
    return render(request, 'flights/boarding_passes.html', {
        'booking': booking,
        'passengers': booking.passengers_info.all(),
    })

@login_required
def download_boarding_pass(request, uuid, passenger_id):
    """Generate and download a PDF boarding pass for a passenger"""
    booking = get_object_or_404(Booking, uuid=uuid, user=request.user)
    passenger = get_object_or_404(Passenger, id=passenger_id, booking=booking)
    
    # Ensure check-in is completed
    if not hasattr(booking, 'check_in') or not booking.check_in.completed:
        messages.error(request, _('Debe completar el check-in primero.'))
        return redirect('flights:booking_detail', uuid=uuid)
    
    # Generate PDF boarding pass (requires additional implementation)
    # Placeholder implementation returns a simple text response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="boarding_pass_{booking.booking_reference}_{passenger.id}.pdf"'
    
    # Use a library like ReportLab to generate the PDF
    # For now, we'll implement a very basic version
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    
    # Add boarding pass content
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "MILLO AIRLINES")
    p.setFont("Helvetica", 12)
    p.drawString(100, 780, f"Boarding Pass - {booking.booking_reference}")
    p.drawString(100, 760, f"Passenger: {passenger.first_name} {passenger.last_name}")
    p.drawString(100, 740, f"Flight: {booking.flight.flight_number}")
    p.drawString(100, 720, f"From: {booking.flight.origin.name}")
    p.drawString(100, 700, f"To: {booking.flight.destination.name}")
    p.drawString(100, 680, f"Date: {booking.flight.departure_time.strftime('%d %b %Y')}")
    p.drawString(100, 660, f"Time: {booking.flight.departure_time.strftime('%H:%M')}")
    p.drawString(100, 640, f"Seat: {passenger.seat_number}")
    
    # Add barcode (placeholder)
    p.setFont("Helvetica", 8)
    p.drawString(100, 620, "SCAN BARCODE AT GATE")
    p.rect(100, 570, 200, 40, stroke=1, fill=0)
    p.drawString(150, 590, f"{booking.booking_reference}|{passenger.document_number}")
    
    p.showPage()
    p.save()
    
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response

@login_required
def download_receipt(request, uuid):
    """Generate and download a PDF receipt for a booking"""
    booking = get_object_or_404(Booking, uuid=uuid, user=request.user)
    
    # Only allow download if payment is completed
    if not booking.payment_status:
        messages.error(request, _('No se puede descargar el recibo si el pago no ha sido completado.'))
        return redirect('flights:booking_detail', uuid=uuid)
    
    # Generate PDF receipt
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{booking.booking_reference}.pdf"'
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    
    # Add receipt content
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "MILLO AIRLINES")
    p.setFont("Helvetica", 12)
    p.drawString(100, 780, f"Receipt - {booking.booking_reference}")
    p.drawString(100, 760, f"Date: {timezone.now().strftime('%d %b %Y')}")
    p.drawString(100, 740, f"Customer: {booking.user.get_full_name() or booking.user.email}")
    p.drawString(100, 720, f"Email: {booking.user.email}")
    
    # Flight details
    p.drawString(100, 680, "FLIGHT DETAILS")
    p.line(100, 675, 500, 675)
    p.drawString(100, 660, f"Flight: {booking.flight.flight_number}")
    p.drawString(100, 640, f"From: {booking.flight.origin.name} ({booking.flight.origin.city}, {booking.flight.origin.country})")
    p.drawString(100, 620, f"To: {booking.flight.destination.name} ({booking.flight.destination.city}, {booking.flight.destination.country})")
    p.drawString(100, 600, f"Departure: {booking.flight.departure_time.strftime('%d %b %Y %H:%M')}")
    p.drawString(100, 580, f"Arrival: {booking.flight.arrival_time.strftime('%d %b %Y %H:%M')}")
    
    # Booking details
    p.drawString(100, 540, "BOOKING DETAILS")
    p.line(100, 535, 500, 535)
    p.drawString(100, 520, f"Passengers: {booking.passengers}")
    p.drawString(100, 500, f"Status: {booking.get_status_display()}")
    p.drawString(100, 480, f"Payment Date: {booking.payment_date.strftime('%d %b %Y') if booking.payment_date else 'N/A'}")
    
    # Pricing
    p.drawString(100, 440, "PRICING")
    p.line(100, 435, 500, 435)
    p.drawString(100, 420, f"Price per passenger: ${booking.flight.price}")
    p.drawString(100, 400, f"Number of passengers: {booking.passengers}")
    p.drawString(100, 380, f"Total price: ${booking.total_price}")
    
    # Footer
    p.setFont("Helvetica", 8)
    p.drawString(100, 100, "Thank you for choosing Millo Airlines!")
    p.drawString(100, 80, "For any inquiries, please contact our customer service at support@milloairlines.com")
    
    p.showPage()
    p.save()
    
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response

class BookingWizardBase(LoginRequiredMixin, FormView):
    """Base class for booking wizard views."""
    
    def dispatch(self, request, *args, **kwargs):
        if 'booking_state' not in request.session:
            request.session['booking_state'] = {
                'step': BookingState.SEARCH.value,
                'search_params': None,
                'selected_flight': None,
                'passenger_data': None,
                'booking_id': None
            }
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_step'] = self.request.session['booking_state']['step']
        return context

class FlightSearchView(BookingWizardBase):
    """First step of the booking process - Flight search."""
    template_name = 'flights/flight_search.html'
    form_class = FlightSearchForm
    success_url = reverse_lazy('flight_selection')

    def get_initial(self):
        """Restore previous search parameters if they exist."""
        initial = super().get_initial()
        booking_state = self.request.session.get('booking_state', {})
        search_params = booking_state.get('search_params')
        
        if search_params:
            initial.update({
                'origin': search_params.get('origin'),
                'destination': search_params.get('destination'),
                'departure_date': datetime.strptime(
                    search_params.get('departure_date'), 
                    '%Y-%m-%d'
                ).date() if search_params.get('departure_date') else None,
                'return_date': datetime.strptime(
                    search_params.get('return_date'),
                    '%Y-%m-%d'
                ).date() if search_params.get('return_date') else None,
                'passengers': search_params.get('passengers', 1)
            })
        return initial

    def form_valid(self, form):
        """Store search parameters in session and proceed to flight selection."""
        booking_state = self.request.session['booking_state']
        booking_state['search_params'] = {
            'origin': form.cleaned_data['origin'].id,
            'destination': form.cleaned_data['destination'].id,
            'departure_date': form.cleaned_data['departure_date'].strftime('%Y-%m-%d'),
            'return_date': form.cleaned_data['return_date'].strftime('%Y-%m-%d') if form.cleaned_data.get('return_date') else None,
            'passengers': form.cleaned_data['passengers']
        }
        booking_state['step'] = BookingState.SELECTION.value
        self.request.session.modified = True
        return super().form_valid(form)

class FlightSelectionView(BookingWizardBase, FormView):
    template_name = 'flights/select_flight.html'
    form_class = FlightSelectionForm
    success_url = reverse_lazy('flights:select_seats')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_params = self.request.session.get('search_params')
        if search_params:
            context['available_flights'] = self.booking_service.get_available_flights(
                origin_id=search_params['origin'],
                destination_id=search_params['destination'],
                departure_date=search_params['departure_date'],
                passengers=search_params['passengers']
            )
        return context

    def form_valid(self, form):
        flight_id = self.request.POST.get('flight_id')
        if not flight_id:
            messages.error(self.request, _('Please select a flight.'))
            return self.form_invalid(form)
        
        self.booking_state.set_flight(flight_id)
        self.booking_state.set_passenger_count(form.cleaned_data['passengers'])
        return super().form_valid(form)

class SeatSelectionView(BookingWizardBase, FormView):
    template_name = 'flights/select_seats.html'
    form_class = SeatSelectionForm
    success_url = reverse_lazy('flights:passenger_details')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        flight = self.booking_service.get_flight(self.booking_state.get_flight_id())
        context.update({
            'flight': flight,
            'available_seats': self.booking_service.get_available_seats(flight),
            'passenger_count': self.booking_state.get_passenger_count()
        })
        return context

    def form_valid(self, form):
        self.booking_state.set_selected_seats(form.cleaned_data['selected_seats'])
        return super().form_valid(form)

class PassengerDetailsView(BookingWizardBase, FormView):
    template_name = 'flights/passenger_details.html'
    success_url = reverse_lazy('flights:payment')

    def get_form(self):
        return PassengerFormSet(
            data=self.request.POST or None,
            initial=self.booking_state.get_passenger_data()
        )

    def form_valid(self, formset):
        passenger_data = []
        for form in formset:
            if form.is_valid():
                passenger_data.append(form.cleaned_data)
        
        self.booking_state.set_passenger_data(passenger_data)
        return super().form_valid(formset)

class PaymentView(BookingWizardBase, FormView):
    template_name = 'flights/payment.html'
    form_class = PaymentForm
    success_url = reverse_lazy('flights:confirmation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        flight = self.booking_service.get_flight(self.booking_state.get_flight_id())
        context['booking_summary'] = {
            'flight': flight,
            'passengers': self.booking_state.get_passenger_count(),
            'total_price': flight.price * self.booking_state.get_passenger_count(),
            'selected_seats': self.booking_state.get_selected_seats()
        }
        return context

    def form_valid(self, form):
        try:
            # Process payment and create booking
            booking = self.booking_service.create_booking(
                user=self.request.user,
                flight_id=self.booking_state.get_flight_id(),
                passenger_data=self.booking_state.get_passenger_data(),
                selected_seats=self.booking_state.get_selected_seats(),
                payment_data=form.cleaned_data
            )
            
            # Clear booking state after successful booking
            self.booking_state.clear()
            
            # Store booking reference for confirmation page
            self.request.session['booking_reference'] = booking.reference
            
            return super().form_valid(form)
            
        except Exception as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

class BookingConfirmationView(BookingWizardBase, TemplateView):
    template_name = 'flights/confirmation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking_reference = self.request.session.get('booking_reference')
        if booking_reference:
            context['booking'] = self.booking_service.get_booking(booking_reference)
            del self.request.session['booking_reference']
        return context

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_flight_list(request):
    flights = Flight.objects.all().order_by('-departure_time')
    return render(request, 'flights/admin/flight_list.html', {
        'flights': flights
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_flight_create(request):
    if request.method == 'POST':
        form = FlightForm(request.POST)
        if form.is_valid():
            flight = form.save()
            messages.success(request, 'Vuelo creado exitosamente.')
            return redirect('flights:admin_flight_list')
    else:
        form = FlightForm()
    
    return render(request, 'flights/admin/flight_form.html', {
        'form': form,
        'title': 'Crear Nuevo Vuelo'
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_flight_edit(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    
    if request.method == 'POST':
        form = FlightForm(request.POST, instance=flight)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vuelo actualizado exitosamente.')
            return redirect('flights:admin_flight_list')
    else:
        form = FlightForm(instance=flight)
    
    return render(request, 'flights/admin/flight_form.html', {
        'form': form,
        'title': 'Editar Vuelo',
        'flight': flight
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_flight_delete(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    
    if request.method == 'POST':
        flight.delete()
        messages.success(request, 'Vuelo eliminado exitosamente.')
        return redirect('flights:admin_flight_list')
    
    return render(request, 'flights/admin/flight_confirm_delete.html', {
        'flight': flight
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_destinations(request):
    destinations = Destination.objects.all().order_by('name')
    return render(request, 'flights/admin/manage_destinations.html', {
        'destinations': destinations
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def destination_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        city = request.POST.get('city')
        country = request.POST.get('country')
        airport_code = request.POST.get('airport_code')
        
        if all([name, city, country, airport_code]):
            Destination.objects.create(
                name=name,
                city=city,
                country=country,
                airport_code=airport_code,
                is_active=True
            )
            messages.success(request, 'Destino creado exitosamente.')
            return redirect('flights:manage_destinations')
        else:
            messages.error(request, 'Por favor complete todos los campos.')
    
    return render(request, 'flights/admin/destination_form.html')

@login_required
@user_passes_test(lambda u: u.is_staff)
def destination_edit(request, destination_id):
    destination = get_object_or_404(Destination, id=destination_id)
    
    if request.method == 'POST':
        destination.name = request.POST.get('name', destination.name)
        destination.city = request.POST.get('city', destination.city)
        destination.country = request.POST.get('country', destination.country)
        destination.airport_code = request.POST.get('airport_code', destination.airport_code)
        destination.is_active = request.POST.get('is_active', 'off') == 'on'
        
        if all([destination.name, destination.city, destination.country, destination.airport_code]):
            destination.save()
            messages.success(request, 'Destino actualizado exitosamente.')
            return redirect('flights:manage_destinations')
        else:
            messages.error(request, 'Por favor complete todos los campos.')
    
    return render(request, 'flights/admin/destination_form.html', {
        'destination': destination
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def destination_delete(request, destination_id):
    destination = get_object_or_404(Destination, id=destination_id)
    
    if request.method == 'POST':
        destination.delete()
        messages.success(request, 'Destino eliminado exitosamente.')
        return redirect('flights:manage_destinations')
    
    return render(request, 'flights/admin/destination_confirm_delete.html', {
        'destination': destination
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_aircraft(request):
    aircraft = Aircraft.objects.all().select_related('aircraft_type').order_by('registration')
    return render(request, 'flights/admin/manage_aircraft.html', {
        'aircraft': aircraft
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def aircraft_create(request):
    if request.method == 'POST':
        registration = request.POST.get('registration')
        aircraft_type_id = request.POST.get('aircraft_type')
        status = request.POST.get('status', 'active')
        
        if all([registration, aircraft_type_id]):
            aircraft_type = get_object_or_404(AircraftType, id=aircraft_type_id)
            Aircraft.objects.create(
                registration=registration,
                aircraft_type=aircraft_type,
                status=status
            )
            messages.success(request, 'Aeronave creada exitosamente.')
            return redirect('flights:manage_aircraft')
        else:
            messages.error(request, 'Por favor complete todos los campos.')
    
    aircraft_types = AircraftType.objects.all()
    return render(request, 'flights/admin/aircraft_form.html', {
        'aircraft_types': aircraft_types
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def aircraft_edit(request, aircraft_id):
    aircraft = get_object_or_404(Aircraft, id=aircraft_id)
    
    if request.method == 'POST':
        registration = request.POST.get('registration')
        aircraft_type_id = request.POST.get('aircraft_type')
        status = request.POST.get('status')
        
        if all([registration, aircraft_type_id, status]):
            aircraft_type = get_object_or_404(AircraftType, id=aircraft_type_id)
            aircraft.registration = registration
            aircraft.aircraft_type = aircraft_type
            aircraft.status = status
            aircraft.save()
            messages.success(request, 'Aeronave actualizada exitosamente.')
            return redirect('flights:manage_aircraft')
        else:
            messages.error(request, 'Por favor complete todos los campos.')
    
    aircraft_types = AircraftType.objects.all()
    return render(request, 'flights/admin/aircraft_form.html', {
        'aircraft': aircraft,
        'aircraft_types': aircraft_types
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def aircraft_delete(request, aircraft_id):
    aircraft = get_object_or_404(Aircraft, id=aircraft_id)
    
    if request.method == 'POST':
        aircraft.delete()
        messages.success(request, 'Aeronave eliminada exitosamente.')
        return redirect('flights:manage_aircraft')
    
    return render(request, 'flights/admin/aircraft_confirm_delete.html', {
        'aircraft': aircraft
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def view_reports(request):
    # Get statistics
    total_flights = Flight.objects.count()
    total_bookings = Booking.objects.count()
    total_revenue = Booking.objects.filter(payment_status=True).aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Get popular routes
    popular_routes = Flight.objects.values(
        'origin__name', 'destination__name'
    ).annotate(
        total_bookings=Count('bookings')
    ).order_by('-total_bookings')[:5]
    
    # Get monthly revenue
    monthly_revenue = Booking.objects.filter(
        payment_status=True
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        revenue=Sum('total_price')
    ).order_by('-month')[:12]
    
    return render(request, 'flights/admin/reports.html', {
        'total_flights': total_flights,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'popular_routes': popular_routes,
        'monthly_revenue': monthly_revenue
    })

@login_required
def booking_process(request, flight_id, step):
    """Handle the booking process steps"""
    flight = get_object_or_404(Flight, id=flight_id)
    
    context = {
        'flight': flight,
        'step': step,
        'passengers': request.session.get('passengers', 1),
    }
    
    if step == 2:  # Seat selection
        if request.method == 'POST':
            selected_seats = request.POST.get('selected_seats', '')
            if selected_seats:
                request.session['selected_seats'] = selected_seats
                return redirect('flights:booking_process', flight_id=flight_id, step=3)
            else:
                messages.error(request, _('Por favor selecciona los asientos requeridos.'))
        selected_seats = request.session.get('selected_seats', '')
        context['selected_seats'] = selected_seats.split(',') if selected_seats else []
    elif step == 3:  # Passenger information
        if not request.session.get('selected_seats'):
            messages.error(request, _('Por favor selecciona los asientos primero.'))
            return redirect('flights:booking_process', flight_id=flight_id, step=2)
        context['passengers_range'] = range(request.session.get('passengers', 1))
        context['selected_seats'] = request.session.get('selected_seats', '').split(',')
    elif step == 4:  # Payment
        if not request.session.get('passenger_data'):
            messages.error(request, _('Por favor completa la información de los pasajeros primero.'))
            return redirect('flights:booking_process', flight_id=flight_id, step=3)
    
    return render(request, 'flights/booking_process.html', context)

@login_required
def booking_confirm(request, flight_id):
    """Handle the booking confirmation and payment processing"""
    flight = get_object_or_404(Flight, id=flight_id)
    
    if request.method == 'POST':
        # Process payment
        payment_method = request.POST.get('payment_method')
        
        try:
            # Create booking
            booking = Booking.objects.create(
                user=request.user,
                flight=flight,
                passengers=request.session.get('passengers', 1),
                total_price=flight.price * request.session.get('passengers', 1),
                status='CONFIRMED',
                payment_status=True,
                payment_date=timezone.now()
            )
            
            # Create passenger records
            passenger_data = request.session.get('passenger_data', [])
            selected_seats = request.session.get('selected_seats', '').split(',')
            
            for i, data in enumerate(passenger_data):
                Passenger.objects.create(
                    booking=booking,
                    first_name=data.get('first_name'),
                    last_name=data.get('last_name'),
                    document_type=data.get('document_type'),
                    document_number=data.get('document_number'),
                    birth_date=data.get('birth_date'),
                    nationality=data.get('nationality'),
                    seat_number=selected_seats[i] if i < len(selected_seats) else None
                )
            
            # Update flight available seats
            flight.available_seats -= booking.passengers
            flight.save()
            
            # Clear booking session data
            for key in ['passengers', 'selected_seats', 'passenger_data']:
                if key in request.session:
                    del request.session[key]
            
            messages.success(request, _('Booking confirmed successfully!'))
            return redirect('flights:booking_detail', uuid=booking.uuid)
            
        except Exception as e:
            messages.error(request, str(e))
            return redirect('flights:booking_process', flight_id=flight_id, step=4)
    
    return redirect('flights:booking_process', flight_id=flight_id, step=4)
