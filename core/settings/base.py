from pathlib import Path
import os
from dotenv import load_dotenv

# Carga variables desde backend/.env (load_dotenv busca hacia arriba)
load_dotenv()

# BASE_DIR apuntará a .../backend
BASE_DIR = Path(__file__).resolve().parents[2]

# Seguridad / Debug
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-insecure-key')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Hosts
ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', '').split(',') if h.strip()]

# Apps base Django
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Terceros
    'rest_framework',
    'corsheaders',
    'apps.catalogos',
    'apps.pedidos',
    'apps.pagos',
    'apps.kds',
    'apps.menus',
    'apps.seguridad',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Debe ir arriba de CommonMiddleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Si luego usas templates del admin o emails internos:
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'

# Base de datos (SQL Server via mssql-django + ODBC Driver 18)
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),           # p.ej. ALDAIR o ALDAIR\SQLEXPRESS
        'PORT': os.getenv('DB_PORT', '1434'),
        'OPTIONS': {
            'driver': 'ODBC Driver 18 for SQL Server',
            # Driver 18 exige cifrado; si usas entorno local, confía el certificado:
            'extra_params': 'TrustServerCertificate=yes',
        },
    }
}

# Zona horaria / idioma
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Guatemala'
USE_I18N = True
USE_TZ = True

# Archivos estáticos
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# DRF (config mínima)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# CORS
CORS_ALLOW_ALL_ORIGINS = os.getenv('CORS_ALLOW_ALL_ORIGINS', 'False') == 'True'
# Si en producción desactivas lo anterior, especifica orígenes:
# CORS_ALLOWED_ORIGINS = [ 'https://tu-front.com', ]
