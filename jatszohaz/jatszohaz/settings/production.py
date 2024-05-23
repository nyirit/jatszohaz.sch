import os
import raven
from os.path import abspath, pardir
from .base import *  # noqa
from .base import INSTALLED_APPS, get_env_variable, DEFAULT_FROM_EMAIL

if 'SENTRY_DSN' in os.environ:
    INSTALLED_APPS += (
        'raven.contrib.django.raven_compat',
    )
    RAVEN_CONFIG = {
        'dsn': get_env_variable('SENTRY_DSN'),
        'release': raven.fetch_git_sha(abspath(pardir)),
    }

# ######### EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = get_env_variable('EMAIL_HOST', 'localhost')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-password
EMAIL_HOST_PASSWORD = get_env_variable('EMAIL_HOST_PASSWORD', '')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-host-user
EMAIL_HOST_USER = get_env_variable('EMAIL_HOST_USER', '')

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = get_env_variable('EMAIL_PORT', 587)

# See: https://docs.djangoproject.com/en/3.1/ref/settings/#std:setting-EMAIL_TIMEOUT
EMAIL_TIMEOUT = 5

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-use-tls
EMAIL_USE_TLS = True

SERVER_EMAIL = get_env_variable('SERVER_EMAIL', DEFAULT_FROM_EMAIL)
# ######### END EMAIL CONFIGURATION

# ######### SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = get_env_variable('DJANGO_SECRET_KEY')
# ######### END SECRET CONFIGURATION

SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
