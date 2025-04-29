import sys
import os

print("Registrando paquetes...")

# Asegurar que el directorio actual está en el path
current_dir = os.path.abspath(os.path.dirname(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
    print(f"Añadido {current_dir} al path")

# Verificar que existe el directorio
templatetags_dir = os.path.join(current_dir, 'accounts', 'templatetags')
print(f"¿Existe el directorio templatetags? {os.path.exists(templatetags_dir)}")

# Listar archivos en el directorio
if os.path.exists(templatetags_dir):
    print("Archivos en el directorio:")
    for file in os.listdir(templatetags_dir):
        print(f" - {file}")

# Intentar importar el módulo
try:
    import accounts.templatetags.custom_filters
    import flights.templatetags.flight_filters
    print("¡Módulos importados con éxito!")
except ImportError as e:
    print(f"Error al importar los módulos: {e}")

print("Proceso completado.") 