"""
Context processors para la aplicación accounts.
"""

def site_settings(request):
    """
    Agrega configuraciones del sitio al contexto de las plantillas.
    """
    return {
        'site_name': 'Millo Airlines',
        'site_description': 'Sistema exclusivo de reserva de vuelos VIP',
        'contact_email': 'info@milloairlines.com',
        'contact_phone': '+57 (1) 123-4567',
        'contact_address': 'Bogotá, Colombia',
    } 