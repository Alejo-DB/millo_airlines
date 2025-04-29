from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_type', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    class UserType(models.TextChoices):
        CLIENT = 'CLIENT', _('Cliente VIP')
        STAFF = 'STAFF', _('Personal')
        ADMIN = 'ADMIN', _('Administrador')

    # Eliminar username y usar solo email
    username = None
    email = models.EmailField(_('email address'), unique=True)
    
    # Campos personalizados
    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.CLIENT,
        verbose_name=_('Tipo de Usuario')
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    phone = models.CharField(_('teléfono'), max_length=20, blank=True)
    birth_date = models.DateField(_('fecha de nacimiento'), null=True, blank=True)
    is_verified = models.BooleanField(_('verificado'), default=False)
    verification_token = models.CharField(_('token de verificación'), max_length=100, null=True, blank=True)
    vip_level = models.PositiveSmallIntegerField(_('nivel VIP'), default=1)
    preferred_destinations = models.JSONField(_('destinos preferidos'), default=list, blank=True)
    last_access = models.DateTimeField(_('último acceso'), auto_now=True)
    
    # Configuración de usuario
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    class Meta:
        verbose_name = _('Usuario')
        verbose_name_plural = _('Usuarios')
        ordering = ['-date_joined']
        permissions = [
            ("access_vip_lounge", "Can access VIP lounge"),
            ("view_flight_history", "Can view flight history"),
            ("manage_bookings", "Can manage bookings"),
        ]

    def __str__(self):
        return f"{self.get_full_name() or self.email} ({self.get_user_type_display()})"

    @property
    def is_admin(self):
        return self.user_type == self.UserType.ADMIN or self.is_superuser

    @property
    def is_staff_member(self):
        return self.user_type == self.UserType.STAFF or self.is_staff

    def get_initials(self):
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        return self.email[0:2].upper()