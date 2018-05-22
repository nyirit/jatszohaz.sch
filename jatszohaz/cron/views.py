from datetime import datetime, timedelta
import logging
from urllib.parse import urljoin
from django.conf import settings
from django.http import HttpResponse
from django.views import View
from jatszohaz.utils import send_slack_message
from rent.models import Rent


logger = logging.getLogger(__name__)


class Run(View):
    http_method_names = ['get', ]

    def get(self, request, *args, **kwargs):
        # check cron token
        if not settings.CRON_TOKEN or not settings.CRON_TOKEN == kwargs.get('token'):
            logger.error("Invalid cron token!")
            return HttpResponse("Invalid token.")

        # send notification about pending rents
        from_date = datetime.now() - timedelta(1)
        rents = Rent.objects.filter(created__lte=from_date).filter(status=Rent.STATUS_PENDING[0])
        if rents:
            context = {'rents':  [urljoin(settings.SITE_DOMAIN, str(r.get_absolute_url()))
                                  for r in rents.all()]}
            send_slack_message('slack/pending_rents.html', context)
            logger.info("Pending rents processed.")

        logger.info("Cron finished.")
        return HttpResponse("OK")
