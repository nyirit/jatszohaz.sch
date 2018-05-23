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

        debug = kwargs.get('arg') == 'debug'
        if debug:
            logger.info("Running in debug mode")

        # send notification about pending rents
        now = datetime.now()
        yesterday = now - timedelta(1)
        rents = (
            # created 24h+ ago, but still pending
            Rent.objects.filter(created__lte=yesterday).filter(status=Rent.STATUS_PENDING[0]) |
            # date_to passed, but still not closed
            Rent.objects.filter(date_to__lte=yesterday).filter(
                status__in=(
                    Rent.STATUS_PENDING[0],
                    Rent.STATUS_APPROVED[0],
                    Rent.STATUS_GAVE_OUT[0])
                ) |
            # date_from passed but not gave out
            Rent.objects.filter(date_from__lte=yesterday).filter(
                status__in=(
                    Rent.STATUS_PENDING[0],
                    Rent.STATUS_APPROVED[0])
                )
            ).distinct()
        if rents:
            context = {'rents': [urljoin(settings.SITE_DOMAIN, str(r.get_absolute_url()))
                                 for r in rents.all()]}
            if debug:
                logger.info("Slack message context: %s" % context)
            else:
                send_slack_message('slack/pending_rents.html', context)
            logger.info("Pending rents processed.")

        logger.info("Finished.")
        return HttpResponse("OK")
