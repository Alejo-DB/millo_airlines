from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FlightsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'flights'
    verbose_name = _('Gestión de Vuelos')
    
    def ready(self):
        import flights.signals
