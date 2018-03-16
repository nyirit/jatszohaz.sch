from .base import *  # noqa

from .base import AUTHENTICATION_BACKENDS, INSTALLED_APPS

DEBUG = True

INSTALLED_APPS += (
    'django_extensions',
    'rosetta',
)

AUTHENTICATION_BACKENDS += ['django.contrib.auth.backends.ModelBackend']
