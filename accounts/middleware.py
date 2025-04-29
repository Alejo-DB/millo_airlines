from django.shortcuts import redirect
from django.urls import resolve, reverse

class AdminRedirectMiddleware:
    """
    Middleware para redireccionar a los administradores al panel de administración.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Procesar la solicitud antes de que la vista sea llamada
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Si el usuario está autenticado, es administrador y está accediendo al dashboard normal
        if request.user.is_authenticated and request.user.is_admin:
            current_url = resolve(request.path_info).url_name
            if current_url == 'user_dashboard':
                return redirect('flights:admin_dashboard')
        return None 