from .base import *  # noqa
from .base import get_env_variable

# TODO
DEBUG = True

# ######### SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = get_env_variable('DJANGO_SECRET_KEY')
# ######### END SECRET CONFIGURATION
