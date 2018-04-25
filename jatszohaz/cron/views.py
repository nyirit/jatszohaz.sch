import logging
from django.conf import settings
from django.http import HttpResponse
from django.views import View


logger = logging.getLogger(__name__)


class Run(View):
    http_method_names = ['get', ]

    def get(self, request, *args, **kwargs):
        if not settings.CRON_TOKEN or not settings.CRON_TOKEN == kwargs.get('token'):
            logger.error("Invalid cron token!")
            return HttpResponse("Invalid token.")

        logger.info("Cron finished successfully.")
        return HttpResponse("OK")
