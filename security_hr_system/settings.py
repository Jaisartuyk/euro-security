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
# Configuración de producción
if not DEBUG:
    # Mantener DEBUG=False en producción para seguridad
    pass

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
    'django.middleware.security.SecurityMiddleware',  # Habilitado para producción
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

# Configuración de base de datos
# Usar URL pública de PostgreSQL que funciona desde Railway CLI
DATABASE_URL = os.environ.get('DATABASE_PUBLIC_URL') or os.environ.get('DATABASE_URL')

if DATABASE_URL:
    try:
        # Configuración para Railway PostgreSQL
        # Parsear URL manualmente: postgresql://user:password@host:port/dbname
        import urllib.parse as urlparse
        url = urlparse.urlparse(DATABASE_URL)
        
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': url.path[1:],  # Remover el '/' inicial
                'USER': url.username,
                'PASSWORD': url.password,
                'HOST': url.hostname,
                'PORT': url.port,
            }
        }
    except Exception as e:
        print(f"Warning: PostgreSQL config failed: {e}")
        # Fallback a SQLite si hay problemas
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
else:
    # Configuración local SQLite
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

# CSRF Cookie settings - Configuración de producción
CSRF_COOKIE_SECURE = not DEBUG  # Seguro en producción (HTTPS)
CSRF_COOKIE_HTTPONLY = False  # Permitir acceso desde JavaScript
CSRF_COOKIE_SAMESITE = 'Lax'

# Configuraciones de seguridad para producción HTTPS
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
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
# Configuración para manejar imágenes base64 grandes
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB para imágenes
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000  # Permitir más campos
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB para archivos

# Configuración de sesiones
SESSION_COOKIE_AGE = 8 * 60 * 60  # 8 horas
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Configuración de seguridad adicional
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
