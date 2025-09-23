"""
Django settings for security_hr_system project.
Sistema de Gestión de Personal para TV Services
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-tvservices-hr-system-2024-security-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
# Temporal: Forzar DEBUG en producción para ver errores
if not DEBUG:
    DEBUG = True  # Temporal para debugging

# ALLOWED_HOSTS - Permitir todos los hosts para Railway
if DEBUG:
    ALLOWED_HOSTS = ['*']  # En desarrollo, permitir todos
else:
    # En producción, permitir dominios específicos y Railway
    ALLOWED_HOSTS = [
        'euro-security-production.up.railway.app',
        'high-pitched-fuel-production.up.railway.app',
        '*.up.railway.app',
        '*.railway.app',
        'localhost',
        '127.0.0.1'
    ]
    
    # Agregar dominios de variables de entorno
    railway_static = os.environ.get('RAILWAY_STATIC_URL')
    railway_public = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
    
    if railway_static:
        ALLOWED_HOSTS.append(railway_static)
    if railway_public:
        ALLOWED_HOSTS.append(railway_public)


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Aplicaciones del sistema
    'core',
    'employees',
    'departments',
    'positions',
    'dashboard',
    'reports',
    'attendance',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'security_hr_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.attendance_permissions',
                'core.context_processors.company_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'security_hr_system.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'es-mx'

TIME_ZONE = 'America/Mexico_City'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

# CSRF Configuration for Railway
CSRF_TRUSTED_ORIGINS = [
    'https://euro-security-production.up.railway.app',
    'https://high-pitched-fuel-production.up.railway.app'
]

# Add Railway domains from environment
railway_static = os.environ.get('RAILWAY_STATIC_URL')
railway_public = os.environ.get('RAILWAY_PUBLIC_DOMAIN')

if railway_static:
    CSRF_TRUSTED_ORIGINS.append(f'https://{railway_static}')
if railway_public:
    CSRF_TRUSTED_ORIGINS.append(f'https://{railway_public}')

# CSRF Cookie settings
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = False  # Permitir acceso desde JavaScript
CSRF_COOKIE_SAMESITE = 'Lax'
LOGOUT_REDIRECT_URL = '/login/'

# Google Maps API
GOOGLE_MAPS_API_KEY = 'AIzaSyAtEPZgbPBwnJGrvIuwplRJDFbr0tmbnyQ'

# Configuración de asistencias
ATTENDANCE_SETTINGS = {
    'ENABLE_GEOLOCATION': True,
    'ENABLE_FACIAL_RECOGNITION': True,
    'DEFAULT_WORK_HOURS': 8,
    'LATE_TOLERANCE_MINUTES': 15,
    'LOCATION_RADIUS_METERS': 100,
}

# Configuración específica para EURO SECURITY
COMPANY_NAME = 'EURO SECURITY'
COMPANY_TAGLINE = 'Seguridad Física Profesional - Guayaquil, Ecuador'
COMPANY_COUNTRY = 'Ecuador'
COMPANY_CITY = 'Guayaquil'

# Configuración de archivos
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Configuración de sesiones
SESSION_COOKIE_AGE = 8 * 60 * 60  # 8 horas
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Configuración de seguridad adicional
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
