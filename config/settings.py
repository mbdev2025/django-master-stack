from pathlib import Path
import os
import secrets
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', secrets.token_urlsafe(50))

DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    
    # Local apps
    'apps.core',
    'apps.energy',
    'apps.payments',
    'apps.automation',
    'apps.audit',
    'apps.analysis',
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

ROOT_URLCONF = 'config.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
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
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny', # Relaxed for dev, strict in prod
    ]
}

# Redirect login to admin for simplicity in DEV
LOGIN_URL = '/admin/login/'

# === ENEDIS CONFIGURATION ===
# Default to Sandbox URLs if not specified in environment
ENEDIS_API_BASE_URL = os.environ.get("ENEDIS_API_BASE_URL", "https://gw.enedis.fr/v1")
ENEDIS_AUTH_URL = os.environ.get("ENEDIS_AUTH_URL", "https://mon-compte-particulier.enedis.fr/dataconnect/v1/oauth2/authorize")
ENEDIS_TOKEN_URL = os.environ.get("ENEDIS_TOKEN_URL", "https://gw.enedis.fr/v1/oauth2/token")
ENEDIS_REDIRECT_URI = os.environ.get("ENEDIS_REDIRECT_URI")
# Optional: Path to client certificate and key for mTLS (if needed in Prod)
ENEDIS_CERT_FILE = os.environ.get("ENEDIS_CERT_FILE", None)
ENEDIS_KEY_FILE = os.environ.get("ENEDIS_KEY_FILE", None)

# === LOGGING CONFIGURATION (Auto-added for Enedis Debug) ===
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'apps.energy.services.enedis_client': {  # Capture logs only for Enedis Client
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
