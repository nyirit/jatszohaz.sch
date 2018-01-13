from .base import *  # noqa
from .base import INSTALLED_APPS
from .base import AUTHENTICATION_BACKENDS

DEBUG = True

INSTALLED_APPS += (
    'django_extensions',
    'rosetta',
)

AUTHENTICATION_BACKENDS += ['django.contrib.auth.backends.ModelBackend']
