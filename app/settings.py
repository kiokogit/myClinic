
import os
from pathlib import Path
import importlib.util
from django.apps import AppConfig


# BASE_DIR should already be defined at the top of your settings.py
from pathlib import Path
import importlib.util


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-t2^y9tvb@_v_ln=ij49d9eb4miz6+kfcm5!mg5tv#=yov*-8bz'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


BASE_DIR = Path(__file__).resolve().parent.parent

# 1. Define the core Django apps
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
]

# 2. Define third-party requirements
THIRD_PARTY_APPS = [
    'rest_framework',
    'django_filters',
    'corsheaders',
]

LOCAL_APPS = []
EXCLUDE_DIRS = {'venv', '.git', '__pycache__', 'static', 'media', 'templates', 'docs', 'migrations'}

for item in BASE_DIR.iterdir():
    if not item.is_dir() or item.name in EXCLUDE_DIRS:
        continue

    apps_py = item / 'apps.py'
    if not apps_py.exists():
        if (item / 'models.py').exists():
            LOCAL_APPS.append(item.name)
        continue

    try:
        spec = importlib.util.spec_from_file_location(f"{item.name}.apps", apps_py)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find the AppConfig class
        app_config = None
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and issubclass(obj, AppConfig) and obj is not AppConfig:
                app_config = obj
                break

        if app_config and hasattr(app_config, 'name'):
            LOCAL_APPS.append(app_config.name)          # This is the correct way
        else:
            LOCAL_APPS.append(item.name)  # fallback

    except Exception:
        LOCAL_APPS.append(item.name)  # fallback on error

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + sorted(LOCAL_APPS)


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'utils.middleware.CustomExceptionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'app.wsgi.application'

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }



# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/staticfiles/'
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), "staticfiles")

MEDIA_URL = '/mediafiles/'
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "mediafiles")

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'Authorization',
    'content-type',
    'JWTAUTH',
    'CPARAMS',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]


REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'utils.exceptions.custom_exception_handler',
    # 'DEFAULT_AUTHENTICATION_CLASSES': ['utils.permissions.JWTAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': [
        'utils.permissions.AuthenticatedUserPermission',
    ],
    'DEFAULT_PAGINATION_CLASS': 'utils.pagination.StandardResultsSetPagination',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter'
    ]
}

APPEND_SLASH = False
AUTH_USER_MODEL = 'acl.CustomUser'



DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

DOCS_ROOT = os.path.join(BASE_DIR, 'site')
