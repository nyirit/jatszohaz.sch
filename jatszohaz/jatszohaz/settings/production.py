import os
from .base import *  # noqa
from .base import INSTALLED_APPS
from .base import get_env_variable

INSTALLED_APPS += (
    'raven.contrib.django.raven_compat',
)

if 'SENTRY_DSN' in os.environ:
    RAVEN_CONFIG = {
        'dsn': get_env_variable('SENTRY_DSN'),
    }

# ######### SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = get_env_variable('DJANGO_SECRET_KEY')
# ######### END SECRET CONFIGURATION
