from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.forms import formset_factory
from .models import Flight, Booking, Destination, Passenger
from django.utils import timezone

User = get_user_model()

class FlightSelectionForm(forms.Form):
    passengers = forms.IntegerField(
        min_value=1,
        max_value=20,
        label=_('Number of Passengers'),
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

class SeatSelectionForm(forms.Form):
    selected_seats = forms.CharField(
        widget=forms.HiddenInput(),
        required=True
    )

    def clean_selected_seats(self):
        seats = self.cleaned_data['selected_seats']
        if not seats:
            raise forms.ValidationError(_('Please select seats for all passengers.'))
        return seats

class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger
        fields = ['first_name', 'last_name', 'document_type', 'document_number', 'birth_date', 'nationality']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'document_number': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
        }

PassengerFormSet = formset_factory(PassengerForm, extra=0)

class PaymentForm(forms.Form):
    PAYMENT_METHODS = [
        ('credit_card', _('Credit Card')),
        ('debit_card', _('Debit Card')),
    ]

    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHODS,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label=_('Payment Method')
    )
    
    card_number = forms.CharField(
        label=_('Card Number'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234 5678 9012 3456'
        })
    )
    
    card_name = forms.CharField(
        label=_('Name on Card'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'JOHN DOE'
        })
    )
    
    card_expiry = forms.CharField(
        label=_('Expiry Date'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/YY'
        })
    )
    
    card_cvv = forms.CharField(
        label=_('CVV'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123'
        })
    )
    
    save_card = forms.BooleanField(
        required=False,
        label=_('Save card for future purchases'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    terms = forms.BooleanField(
        required=True,
        label=_('I accept the terms and conditions'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean_card_number(self):
        number = self.cleaned_data['card_number'].replace(' ', '')
        if not number.isdigit() or len(number) < 13 or len(number) > 19:
            raise forms.ValidationError(_('Please enter a valid card number.'))
        return number

    def clean_card_expiry(self):
        expiry = self.cleaned_data['card_expiry']
        if not '/' in expiry:
            raise forms.ValidationError(_('Please enter the expiry date in MM/YY format.'))
        return expiry

    def clean_card_cvv(self):
        cvv = self.cleaned_data['card_cvv']
        if not cvv.isdigit() or len(cvv) < 3 or len(cvv) > 4:
            raise forms.ValidationError(_('Please enter a valid CVV.'))
        return cvv

class FlightSearchForm(forms.Form):
    origin = forms.ModelChoiceField(
        queryset=Destination.objects.filter(is_active=True),
        label=_('Origin'),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'placeholder': _('Select origin')
        })
    )
    
    destination = forms.ModelChoiceField(
        queryset=Destination.objects.filter(is_active=True),
        label=_('Destination'),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'placeholder': _('Select destination')
        })
    )
    
    departure_date = forms.DateField(
        label=_('Departure Date'),
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': timezone.now().date().isoformat()
        })
    )
    
    passengers = forms.IntegerField(
        min_value=1,
        max_value=9,
        initial=1,
        label=_('Passengers'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '9'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        origin = cleaned_data.get('origin')
        destination = cleaned_data.get('destination')
        departure_date = cleaned_data.get('departure_date')
        passengers = cleaned_data.get('passengers')
        
        if origin and destination and origin == destination:
            raise forms.ValidationError(_('Origin and destination cannot be the same.'))
        
        if departure_date:
            if departure_date < timezone.now().date():
                raise forms.ValidationError(_('Departure date cannot be in the past.'))
            
            # No permitir fechas más allá de 1 año
            max_date = timezone.now().date() + timezone.timedelta(days=365)
            if departure_date > max_date:
                raise forms.ValidationError(_('Departure date cannot be more than 1 year in advance.'))
        
        if passengers and passengers > 9:
            raise forms.ValidationError(_('Maximum number of passengers per booking is 9.'))
        
        return cleaned_data

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['passengers', 'special_requests']
        labels = {
            'passengers': _('Número de pasajeros'),
            'special_requests': _('Solicitudes especiales')
        }
        widgets = {
            'special_requests': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        self.flight = kwargs.pop('flight', None)
        super().__init__(*args, **kwargs)
        
        if self.flight:
            self.fields['passengers'].widget.attrs.update({
                'min': 1,
                'max': self.flight.available_seats
            })
            self.fields['passengers'].help_text = _(
                f'Máximo {self.flight.available_seats} pasajeros disponibles'
            )

    def clean_passengers(self):
        passengers = self.cleaned_data.get('passengers')
        if self.flight and passengers > self.flight.available_seats:
            raise forms.ValidationError(
                _('No hay suficientes asientos disponibles para esta cantidad de pasajeros')
            )
        return passengers

class UserPreferencesForm(forms.ModelForm):
    preferred_destinations = forms.ModelMultipleChoiceField(
        queryset=Destination.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Preferred Destinations'
    )

    class Meta:
        model = User
        fields = ['preferred_destinations']

class FlightForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields = [
            'origin', 'destination', 'aircraft', 'departure_time', 
            'arrival_time', 'price', 'status', 'max_passengers'
        ]
        widgets = {
            'departure_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'arrival_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'price': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'max_passengers': forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        departure_time = cleaned_data.get('departure_time')
        arrival_time = cleaned_data.get('arrival_time')
        aircraft = cleaned_data.get('aircraft')
        
        if departure_time and arrival_time:
            if arrival_time <= departure_time:
                raise forms.ValidationError("La hora de llegada debe ser posterior a la hora de salida.")
            
            # Check if aircraft is available
            if aircraft:
                overlapping_flights = Flight.objects.filter(
                    aircraft=aircraft,
                    departure_time__lt=arrival_time,
                    arrival_time__gt=departure_time
                ).exclude(pk=self.instance.pk if self.instance else None)
                
                if overlapping_flights.exists():
                    raise forms.ValidationError("El avión ya está asignado a otro vuelo en ese horario.")
                
                # Set max_passengers based on aircraft capacity
                cleaned_data['max_passengers'] = aircraft.aircraft_type.capacity
        
        return cleaned_data