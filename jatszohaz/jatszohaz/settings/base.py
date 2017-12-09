"""
Django settings for jatszohaz project.

Generated by 'django-admin startproject' using Django 1.11.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

from os import environ

from os.path import dirname, abspath, join, basename, normpath

# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
from django.core.exceptions import ImproperlyConfigured


def get_env_variable(var_name, default=None):
    """ Get the environment variable or return exception/default """
    try:
        return environ[var_name]
    except KeyError:
        if default is None:
            error_msg = "Set the %s environment variable" % var_name
            raise ImproperlyConfigured(error_msg)
        else:
            return default


# ####### PATH CONFIGURATION
# Absolute filesystem path to the Django project directory:
BASE_DIR = dirname(dirname(abspath(__file__)))

# Absolute filesystem path to the top-level project folder:
SITE_ROOT = dirname(BASE_DIR)

# Site name:
SITE_NAME = basename(BASE_DIR)

# ####### END PATH CONFIGURATION


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^e&6xsn6awyd&xz6&gq47$e7lrum18hrlxjicb_!95ky*r*%o5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# HOST CONFIGURATION
# See: https://docs.djangoproject.com/en/1.5/releases/1.5/#allowed-hosts-required-in-production
ALLOWED_HOSTS = get_env_variable('DJANGO_ALLOWED_HOSTS', "*").split(',')
# END HOST CONFIGURATION


# Application definition

DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

THIRD_PARTY_APPS = (
    'social_django',
    'easy_thumbnails',
)

LOCAL_APPS = (
    'authsch',  # currently it's used as local app
    'web',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'jatszohaz.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            normpath(join(SITE_ROOT, 'templates')),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'web.context_processors.default_context_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'jatszohaz.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.' + get_env_variable('DJANG_DB_TYPE', 'postgresql_psycopg2'),
        'NAME':  get_env_variable('DJANGO_DB_NAME'),
        'USER':  get_env_variable('DJANGO_DB_USER'),
        'PASSWORD':  get_env_variable('DJANGO_DB_PASSWORD'),
        'HOST': get_env_variable('DJANGO_DB_HOST', ''),
        'PORT': get_env_variable('DJANGO_DB_PORT', ''),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
]

AUTH_USER_MODEL = 'web.JhUser'

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# ######### STATIC FILE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = normpath(join(SITE_ROOT, 'static_collected'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# See: https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-MEDIA_ROOT
MEDIA_ROOT = normpath(join(SITE_ROOT, '../../site-media/'))

MEDIA_URL = '/media/'

# ######### END STATIC FILE CONFIGURATION


# ######### AUTH.SCH CONFIGURATION
SOCIAL_AUTH_URL_NAMESPACE = 'social'
AUTHENTICATION_BACKENDS = [
   'authsch.authentication.AuthSCHOAuth2',
   'django.contrib.auth.backends.ModelBackend',
]
SOCIAL_AUTH_AUTHSCH_KEY = get_env_variable('AUTHSCH_KEY', '')
SOCIAL_AUTH_AUTHSCH_SECRET = get_env_variable('AUTHSCH_SECRET', '')
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
SOCIAL_AUTH_BACKEND = 'authsch'
LOGIN_URL = "login/%s/" % SOCIAL_AUTH_BACKEND
# ######### END AUTH.SCH CONFIGURATION

EDU_PERSON_ENTITLEMENT_ID = int(get_env_variable('DJANGO_ENTITLEMENT_ID', '-1'))
