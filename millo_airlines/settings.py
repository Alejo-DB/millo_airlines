import os
from pathlib import Path
from datetime import timedelta

# Configuración de seguridad (para desarrollo - en producción usar variables de entorno)
BASE_DIR = Path(__file__).resolve().parent.parent

# Intentar importar decouple, pero si falla usar alternativas seguras
try:
    from decouple import config, Csv
    SECRET_KEY = config('SECRET_KEY', default='django-insecure-!milloairlines!replacewithrealsecretinprod')
    DEBUG = config('DEBUG', default=True, cast=bool)
    ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*', cast=Csv())
except ImportError:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-!milloairlines!replacewithrealsecretinprod')
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'
    ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# Configuración de URL principal
ROOT_URLCONF = 'millo_airlines.urls'
WSGI_APPLICATION = 'millo_airlines.wsgi.application'

# Configuración de aplicaciones premium
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # Apps propias
    'accounts.apps.AccountsConfig',
    'flights.apps.FlightsConfig',
    
    # Apps de terceros
    'crispy_forms',
    'crispy_bootstrap5',
]

# Apps opcionales que pueden estar o no instaladas
OPTIONAL_APPS = [
    'django_tables2',
    'django_filters',
    'widget_tweaks',
    'auditlog',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.apple',
]

# Añadir solo las apps opcionales que estén instaladas
for app in OPTIONAL_APPS:
    try:
        __import__(app.split('.')[0])
        INSTALLED_APPS.append(app)
    except ImportError:
        pass

# Middleware de seguridad profesional
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.AdminRedirectMiddleware',
]

# Middleware opcional para auditoria (si está instalado)
try:
    import auditlog
    MIDDLEWARE.append('auditlog.middleware.AuditlogMiddleware')
except ImportError:
    pass

# Middleware opcional para allauth (si está instalado)
try:
    import allauth.account
    MIDDLEWARE.append('allauth.account.middleware.AccountMiddleware')
except ImportError:
    pass

# Configuración de templates con contexto profesional
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'accounts/templates'),
            os.path.join(BASE_DIR, 'flights/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.context_processors.site_settings',
            ],
            'libraries': {
                'account_filters': 'accounts.templatetags.custom_filters',
                'flight_filters': 'flights.templatetags.flight_filters',
            },
        },
    },
]

# Configuración de base de datos (SQLite para desarrollo, PostgreSQL para producción)
try:
    import dj_database_url
    from decouple import config
    if config('DATABASE_URL', default=''):
        # Configuración para producción
        DATABASES = {
            'default': dj_database_url.config(
                default=config('DATABASE_URL')
            )
        }
    else:
        # Configuración para desarrollo
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
except ImportError:
    # Si no hay dj_database_url o decouple, siempre usar SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Configuración de autenticación optimizada
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Configuración de allauth optimizada
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # Cambiado a optional para no retrasar el login
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None

# Configuración de sesiones optimizada
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 1209600  # 2 semanas
SESSION_SAVE_EVERY_REQUEST = False  # Optimización de rendimiento
SESSION_COOKIE_SECURE = False if DEBUG else True

# Configuración de caché
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Configuración de crispy forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Configuración de seguridad adicional
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Configuración de email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
try:
    from decouple import config
    EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
except ImportError:
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

try:
    from decouple import config
    DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@milloairlines.com')
except ImportError:
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@milloairlines.com')

# Configuración de django-allauth (solo si está instalado)
try:
    import allauth
    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend',
        'allauth.account.auth_backends.AuthenticationBackend',
    ]

    # Configuración básica de allauth
    ACCOUNT_EMAIL_REQUIRED = True
    ACCOUNT_AUTHENTICATION_METHOD = 'email'
    ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
    ACCOUNT_UNIQUE_EMAIL = True
    ACCOUNT_USERNAME_REQUIRED = False
    ACCOUNT_USER_MODEL_USERNAME_FIELD = None
    
    # Formularios personalizados
    ACCOUNT_FORMS = {
        'signup': 'accounts.forms.CustomSignupForm',
    }
    
    # URLs de redirección
    LOGIN_REDIRECT_URL = 'flights:user_dashboard'
    ACCOUNT_LOGOUT_REDIRECT_URL = 'flights:home'
    
    # Configuración de emails
    ACCOUNT_EMAIL_SUBJECT_PREFIX = '[Millo Airlines] '
    ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
    ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
    ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300
    
    # Configuración de contraseñas
    ACCOUNT_PASSWORD_MIN_LENGTH = 8
    ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
    
    # Configuración de sesión
    ACCOUNT_SESSION_REMEMBER = True
    ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
    
except ImportError:
    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend',
    ]

# Configuración de archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Configuración de archivos multimedia
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configuración de idioma y zona horaria
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Configuración del modelo de usuario personalizado
AUTH_USER_MODEL = 'accounts.CustomUser'

# Configuración de archivos estáticos para desarrollo
if DEBUG:
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static'),
    ]
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')