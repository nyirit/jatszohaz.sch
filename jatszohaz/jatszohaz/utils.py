import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django_slack import slack_message
from django.views.generic import UpdateView

logger = logging.getLogger(__name__)


def jh_send_mail(subject, html_message, recipient_list, fail_silently=False):
    message = strip_tags(html_message.replace("<br/>", "\n"))
    msg = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
    msg.attach_alternative(html_message, "text/html")
    msg.send(fail_silently=fail_silently)
    logger.info("Email sent to: %s" % recipient_list)


def send_slack_message(template, context=None):
    try:
        slack_message(template, context, fail_silently=False)
    except Exception as e:
        logger.error("Failed to send slack message: %s" % e)


class DefaultUpdateView(UpdateView):
    """
    Adds default template and some context data.
    """

    template_name = "default_update.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # add some fields to context if they are available
        try:
            context['title'] = self.title
        except AttributeError:
            pass

        try:
            context['success_url'] = self.success_url
        except AttributeError:
            pass
        return context
