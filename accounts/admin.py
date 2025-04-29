from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
from .forms import CustomUserChangeForm, CustomUserCreationForm

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'is_active', 'is_verified')
    list_filter = ('user_type', 'is_active', 'is_verified', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    readonly_fields = ('uuid', 'date_joined', 'last_login')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Information'), {'fields': ('first_name', 'last_name', 'phone', 'birth_date')}),
        (_('Permissions'), {'fields': ('user_type', 'is_active', 'is_verified', 'is_staff', 'is_superuser')}),
        (_('Preferences'), {'fields': ('vip_level', 'preferred_destinations')}),
        (_('Important Dates'), {'fields': ('last_login', 'date_joined'), 'classes': ('collapse',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'user_type', 'is_active', 'is_staff'),
        }),
    )