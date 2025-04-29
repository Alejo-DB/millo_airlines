from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings
import uuid
import json

from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm

def register(request):
    """Vista para el registro de nuevos usuarios"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Generar token de verificación
            token = str(uuid.uuid4())
            user.verification_token = token
            
            # En desarrollo, el usuario es activo pero aún enviamos correo
            if settings.DEBUG:
                user.is_active = True  # Podemos acceder sin verificar en desarrollo
            else:
                user.is_active = False  # Usuario inactivo hasta verificación
            
            user.save()
            
            # Enviar email de verificación (siempre, incluso en desarrollo)
            subject = _('Verifica tu cuenta en Millo Airlines')
            message = render_to_string('accounts/email/verification_email.html', {
                'user': user,
                'token': token,
                'site_name': 'Millo Airlines',
                'request': request,
            })
            
            try:
                sent = send_mail(
                    subject,
                    strip_tags(message),  # Versión plain text
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=message,
                    fail_silently=False,
                )
                
                print(f"Intentando enviar email a {user.email}. Resultado: {sent}")
                
                if sent > 0:
                    if settings.DEBUG:
                        messages.success(request, _(f'Registro exitoso. Email de verificación enviado a {user.email} (en desarrollo, puedes iniciar sesión sin verificar).'))
                    else:
                        messages.success(request, _(f'Registro exitoso. Por favor, verifica tu email {user.email} para activar tu cuenta.'))
                else:
                    messages.warning(request, _('Registro exitoso pero hubo un problema al enviar el email de verificación. Contacta a soporte.'))
            except Exception as e:
                print(f"Error al enviar email: {e}")
                messages.warning(request, _(f'Registro exitoso pero hubo un problema al enviar el email de verificación: {str(e)}'))
            
            return redirect('login')
        else:
            # Mostrar errores detallados
            print("Errores en el formulario:", form.errors)
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)

def verify_email(request, token):
    """Vista para verificar el email del usuario"""
    try:
        user = CustomUser.objects.get(verification_token=token)
        user.is_active = True
        user.verification_token = None
        user.save()
        
        messages.success(request, _('Tu cuenta ha sido verificada. Ahora puedes iniciar sesión.'))
        return redirect('login')
    except CustomUser.DoesNotExist:
        messages.error(request, _('Token de verificación inválido o expirado.'))
        return redirect('login')

def resend_verification(request):
    """Vista para reenviar el email de verificación"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email, is_active=False)
            
            # Generar nuevo token
            token = str(uuid.uuid4())
            user.verification_token = token
            user.save()
            
            # Enviar email de verificación
            subject = _('Verifica tu cuenta en Millo Airlines')
            message = render_to_string('accounts/email/verification_email.html', {
                'user': user,
                'token': token,
                'site_name': 'Millo Airlines',
            })
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=message,
            )
            
            messages.success(request, _('Email de verificación reenviado. Por favor, verifica tu bandeja de entrada.'))
            return redirect('login')
        except CustomUser.DoesNotExist:
            messages.error(request, _('No se encontró una cuenta pendiente de verificación con ese email.'))
    
    return render(request, 'accounts/resend_verification.html')

@login_required
def profile(request):
    """Vista para ver el perfil del usuario"""
    return render(request, 'accounts/profile.html')

@login_required
def edit_profile(request):
    """Vista para editar el perfil del usuario"""
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Perfil actualizado exitosamente.'))
            return redirect('accounts:profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'accounts/edit_profile.html', context)

@login_required
def change_password(request):
    """Vista para cambiar la contraseña del usuario"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, _('Tu contraseña ha sido actualizada exitosamente.'))
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'accounts/change_password.html', context)
