from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from allauth.account.forms import SignupForm
from .models import CustomUser

class CustomSignupForm(SignupForm):
    first_name = forms.CharField(
        max_length=30,
        label=_('First Name'),
        required=True,
        widget=forms.TextInput(attrs={'placeholder': _('Enter your first name')})
    )
    last_name = forms.CharField(
        max_length=30,
        label=_('Last Name'),
        required=True,
        widget=forms.TextInput(attrs={'placeholder': _('Enter your last name')})
    )
    phone = forms.CharField(
        max_length=20,
        label=_('Phone Number'),
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('Enter your phone number')})
    )
    birth_date = forms.DateField(
        label=_('Date of Birth'),
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'placeholder': 'YYYY-MM-DD'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = _('Email Address')
        self.fields['email'].widget.attrs['placeholder'] = _('Enter your email address')
        self.fields['password1'].label = _('Password')
        self.fields['password2'].label = _('Confirm Password')
        self.fields['password1'].widget.attrs['placeholder'] = _('Create a password')
        self.fields['password2'].widget.attrs['placeholder'] = _('Repeat your password')

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.birth_date = self.cleaned_data['birth_date']
        user.save()
        return user

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'phone', 'birth_date')
        widgets = {
            'birth_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'YYYY-MM-DD'}
            ),
            'phone': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': '+1 (123) 456-7890'}
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Improve user experience with clearer messages
        self.fields['email'].help_text = "Enter a valid email address. This will be your login username."
        self.fields['password1'].help_text = "Your password must contain at least 8 characters and cannot be similar to your personal information."
        self.fields['birth_date'].help_text = "Select your birth date using the calendar."
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'CLIENT'  # Ensure all new users are of type CLIENT
        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'phone', 'birth_date')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        } 