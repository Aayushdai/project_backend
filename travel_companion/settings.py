import os
from pathlib import Path
from datetime import timedelta

# ========================
# BASE DIR
# ========================
BASE_DIR = Path(__file__).resolve().parent.parent

# ========================
# SECURITY
# ========================
SECRET_KEY = 'django-insecure-33a!xk@x1n43*g-cg=9+(nnpcd+_m%xtuscg#0p(%6^0n#lnui'

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# ========================
# CORS (React connection)
# ========================
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# ========================
# INSTALLED APPS
# ========================
INSTALLED_APPS = [
    'jazzmin',
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.inlines",
    "unfold.contrib.import_export",

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'channels',
    'corsheaders',

    'apps.trips',
    'apps.chat',
    'apps.expenses',
    'apps.users.apps.UsersConfig',

    'core',
]

# ========================
# MIDDLEWARE
# ========================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ========================
# URLS & TEMPLATES
# ========================
ROOT_URLCONF = 'travel_companion.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ========================
# CHANNELS (WebSocket)
# ========================
ASGI_APPLICATION = 'travel_companion.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

WSGI_APPLICATION = 'travel_companion.wsgi.application'

# ========================
# DATABASE (SQLite)
# ========================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ========================
# REST FRAMEWORK + JWT
# ========================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# ========================
# JAZZMIN ADMIN UI
# ========================
JAZZMIN_SETTINGS = {
    "site_title": "Travel Companion Admin",
    "site_header": "Travel Companion",
    "welcome_sign": "Welcome to Travel Companion Admin",
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users",
    },
    "order_with_respect_to": [
        "auth",
        "users",
        "core",
        "trips",
        "expenses",
    ],
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": True,
    "body_small_text": False,
    "brand_color": "#1e3a8a",
    "accent": "accent-primary",
    "rounded_corners": True,
}

# ========================
# PASSWORD VALIDATION
# ========================
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

# ========================
# INTERNATIONALIZATION
# ========================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'

USE_I18N = True
USE_TZ = True

# ========================
# STATIC FILES (FIXED)
# ========================
STATIC_URL = "/static/"

# Your static files (CSS, JS, images)
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Collected static files (for deployment)
STATIC_ROOT = BASE_DIR / "staticfiles"

# ========================
# MEDIA FILES (UPLOADS)
# ========================
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "mediafiles"

# ========================
# DEFAULT FIELD
# ========================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# settings.py

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB (for file uploads)