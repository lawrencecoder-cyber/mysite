"""
Django settings for mysite project.
Production-ready configuration for Render deployment.
"""

from pathlib import Path
import os
import dj_database_url
from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent

# ========================
# SECURITY
# ========================

# ❗ NEVER hardcode secret key
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

#if not SECRET_KEY:
    #raise ValueError("DJANGO_SECRET_KEY is not set!")

# Debug should always be False in production
DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")

# ========================
# APPLICATIONS
# ========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog',
]

# ========================
# MIDDLEWARE
# ========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',

    # CSRF protection
    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    # Clickjacking protection
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
# ======================
# URLS / WSGI
# ========================
ROOT_URLCONF = 'mysite.urls'
WSGI_APPLICATION = 'mysite.wsgi.application'
# ======================
# CHANNELS
# ======================
ASGI_APPLICATION = "mysite.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.getenv("REDIS_URL")],
        },
    },
}
# ======================
# CELERY
# ======================
CELERY_BROKER_URL = os.getenv("REDIS_URL")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
# ========================

CELERY_BEAT_SCHEDULE = {
    "update-stocks-every-5-sec": {
        "task": "stocks.tasks.update_stocks",
        "schedule": 5.0,
    },
}
# ========================
# TEMPLATES
# ========================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates",  # better for scaling
                 BASE_DIR / "frontend" / "build",  # ✅ React build here
        ],
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
    os.path.join(BASE_DIR, "frontend/build") # React build
]

# ========================
# DATABASE
# ========================
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ========================
# PASSWORD VALIDATION
# ========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ========================
# INTERNATIONALIZATION
# ========================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True
USE_TZ = True

# ========================
# STATIC FILES
# ========================
STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "static",
    BASE_DIR / "frontend" / "build" / "static",
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ========================
# SECURITY HARDENING
# ========================

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Force HTTPS
SECURE_SSL_REDIRECT = True

# Cookies over HTTPS only
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Prevent JS access to cookies
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# HSTS (forces browser to always use HTTPS)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Prevent clickjacking
X_FRAME_OPTIONS = 'DENY'

# Content sniffing protection
SECURE_CONTENT_TYPE_NOSNIFF = True

# Browser XSS protection
SECURE_BROWSER_XSS_FILTER = True

# ========================
# LOGGING (Optional but recommended)
# ========================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
}
