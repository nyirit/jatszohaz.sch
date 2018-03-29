from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags


def jh_send_mail(subject, html_message, recipient_list, fail_silently=False):
    message = strip_tags(html_message.replace("<br/>", "\n"))
    msg = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
    msg.attach_alternative(html_message, "text/html")
    msg.send(fail_silently=fail_silently)
