import os
import sys
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Add apps directory to sys.path so apps can be referenced cleanly if needed
sys.path.insert(0, str(BASE_DIR / 'apps'))

SECRET_KEY = config('DJANGO_SECRET_KEY', default='django-insecure-default-key-change-me')

DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost,.onrender.com', cast=lambda v: [s.strip() for s in v.split(',') if s.strip()])

# Automatically support Render external hostnames and onrender.com subdomains
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
if '.onrender.com' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('.onrender.com')

# CSRF Trusted Origins for Render HTTPS domains
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'http://127.0.0.1',
    'http://localhost',
]
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f'https://{RENDER_EXTERNAL_HOSTNAME}')


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'rest_framework',

    # Local apps
    'apps.core.apps.CoreConfig',
    'apps.accounts.apps.AccountsConfig',
    'apps.buyers.apps.BuyersConfig',
    'apps.campaigns.apps.CampaignsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
ASGI_APPLICATION = 'config.asgi.application'

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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# API Keys & Quotas
GEOAPIFY_API_KEY = config('GEOAPIFY_API_KEY', default='')
HUNTER_API_KEY = config('HUNTER_API_KEY', default='')

EMAIL_PROVIDER = config('EMAIL_PROVIDER', default='console')
BREVO_API_KEY = config('BREVO_API_KEY', default='')
RESEND_API_KEY = config('RESEND_API_KEY', default='')

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@homedecorbuyerfinder.com')
DEFAULT_FROM_NAME = config('DEFAULT_FROM_NAME', default='Home Decor Buyer Finder')
SENDER_POSTAL_ADDRESS = config('SENDER_POSTAL_ADDRESS', default='123 Main Street, Suite 400, Austin, TX 78701')

MAX_BUYERS_PER_SEARCH = config('MAX_BUYERS_PER_SEARCH', default=30, cast=int)
HUNTER_MONTHLY_BUDGET = config('HUNTER_MONTHLY_BUDGET', default=50, cast=int)
EMAIL_DAILY_LIMIT = config('EMAIL_DAILY_LIMIT', default=300, cast=int)

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/search/'
LOGOUT_REDIRECT_URL = '/login/'
