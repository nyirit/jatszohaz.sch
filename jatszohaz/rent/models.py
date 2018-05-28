from datetime import datetime
import logging
from urllib.parse import urljoin
from django.conf import settings
from django.db import models
from django.db.models import Count
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel
from inventory.models import GamePiece
from jatszohaz.models import JhUser
from jatszohaz.utils import jh_send_mail


logger = logging.getLogger(__name__)


class Rent(TimeStampedModel):
    STATUS_PENDING = ("pending", _("Pending"))
    STATUS_APPROVED = ("approved", _("Approved"))
    STATUS_GAVE_OUT = ("gaveout", _("Gave out"))
    STATUS_IN_MY_ROOM = ("inmyroom", _("In my room"))
    STATUS_BACK = ("back", _("Brought back"))
    STATUS_DECLINED = ("declined", _("Declined"))
    STATUS_CANCELLED = ("cancelled", _("Cancelled"))
    STATUS_CHANGE_VERB = {
        "pending": _("Pending"),
        "approved": _("Approve"),
        "gaveout": _("Give out"),
        "inmyroom": _("In my room"),
        "back": _("Bring back"),
        "declined": _("Decline"),
        "cancelled": _("Cancel")
    }
    STATUS_CHOICES = (
        STATUS_PENDING,
        STATUS_APPROVED,
        STATUS_GAVE_OUT,
        STATUS_IN_MY_ROOM,
        STATUS_BACK,
        STATUS_DECLINED,
        STATUS_CANCELLED
    )

    renter = models.ForeignKey(JhUser, on_delete=models.PROTECT, verbose_name=_("Renter"), related_name="rents")
    games = models.ManyToManyField(GamePiece, verbose_name=_("Games"), related_name="rents")
    date_from = models.DateTimeField(verbose_name=_("From"), blank=False, null=False)
    date_to = models.DateTimeField(verbose_name=_("To"), blank=False, null=False)
    status = models.CharField(verbose_name=_("Status"), choices=STATUS_CHOICES,
                              default=STATUS_PENDING[0], max_length=20)
    bail = models.CharField(verbose_name=_("Bail"), max_length=30, blank=True)

    def __str__(self):
        return "%s (%s - %s)" % (self.renter.full_name2(), self.date_from, self.date_to)

    class Meta:
        permissions = (
            ('manage_rents', _('Manage rents')),
            ('view_stat', _('View rent statistics')),
        )

    def get_absolute_url(self):
        return reverse_lazy("rent:details", kwargs={'pk': self.pk})

    def create_new_history(self, user, new_status=None, new_renter=None, added_game=None, deleted_game=None,
                           edited_date_from=None, edited_date_to=None):
        RentHistory.objects.create(user=user,
                                   new_status=new_status,
                                   rent=self,
                                   new_renter=new_renter,
                                   added_game=added_game,
                                   deleted_game=deleted_game,
                                   edited_date_from=edited_date_from,
                                   edited_date_to=edited_date_to)

    def is_past_due(self):
        return ((self.date_to < datetime.now() and self.status == Rent.STATUS_GAVE_OUT[0])
                or (self.date_from < datetime.now() and
                    self.status in (Rent.STATUS_PENDING[0], Rent.STATUS_APPROVED[0])))

    def notify_users(self, subject, message, user_exclude):
        recipient_list = set([c.user.email for c in self.comments.all()] +
                             [self.renter.email, ] +
                             [h.user.email for h in self.histories.all()])
        recipient_list.discard(user_exclude.email)

        if recipient_list:
            url = urljoin(settings.SITE_DOMAIN, str(self.get_absolute_url()))
            subject = settings.EMAIL_SUBJECT_PREFIX + str(subject)
            message += _("You can check your rent here: <a href=\"%s\">%s<a><br/>"
                         "Please do not reply to this email.<br/><br/>"
                         "Best wishes,<br/>Játszóház") % (url, url)
            try:
                jh_send_mail(subject, message, recipient_list)
            except Exception as e:
                logger.error("Failed to send email! %s" % e)
                return False

        return True

    def notify_new_status(self, user):
        subject = _("new status")
        message = _("Hi!<br/><br/>Status of your rent was changed to %s.<br/><br/>") % self.get_status_display()

        return self.notify_users(subject, message, user)

    def notify_new_comment(self, comment):
        subject = _("new comment")
        message = _("Hi!<br/><br/>There is a new comment to your rent.<br/><br/>"
                    "User: %s<br/>Message:<br/>%s<br/>") % (comment.user.full_name2(), comment.message)

        return self.notify_users(subject, message, comment.user)

    def notify_changed_date(self, user):
        subject = _("date changed")
        message = _("Hi!<br/><br/>Your rent date changed.<br/><br/>"
                    "New dates: %s - %s<br/>") % (self.date_from, self.date_to)

        return self.notify_users(subject, message, user)

    def get_status_css(self):
        if self.is_past_due():
            return 'danger'

        if self.status in (Rent.STATUS_APPROVED[0], Rent.STATUS_BACK[0], Rent.STATUS_GAVE_OUT[0]):
            return 'success'

        if self.status == Rent.STATUS_PENDING[0]:
            return 'warning'

        return 'info'

    @staticmethod
    def get_count_by_status():
        status_counts = dict()

        for x in Rent.objects.all().values('status').annotate(total=Count('status')):
            status_counts[x['status']] = x['total']

        return status_counts

    def get_available_statuses(self, user):
        """get available statuses based on current status, i.e. what can be next."""

        available_statuses = []
        if user.has_perm('rent.manage_rents'):
            if self.status in (Rent.STATUS_DECLINED[0], Rent.STATUS_CANCELLED[0], Rent.STATUS_PENDING[0]):
                s = Rent.STATUS_APPROVED[0]
                available_statuses.append((s, Rent.STATUS_CHANGE_VERB[s]))

            if self.status == Rent.STATUS_APPROVED[0]:
                s = Rent.STATUS_GAVE_OUT[0]
                available_statuses.append((s, Rent.STATUS_CHANGE_VERB[s]))

            if self.status == Rent.STATUS_GAVE_OUT[0]:
                s = Rent.STATUS_IN_MY_ROOM[0]
                available_statuses.append((s, Rent.STATUS_CHANGE_VERB[s]))

            if self.status in (Rent.STATUS_IN_MY_ROOM[0], Rent.STATUS_GAVE_OUT[0]):
                s = Rent.STATUS_BACK[0]
                available_statuses.append((s, Rent.STATUS_CHANGE_VERB[s]))

            if self.status in (Rent.STATUS_PENDING[0], Rent.STATUS_APPROVED[0]):
                s = Rent.STATUS_DECLINED[0]
                available_statuses.append((s, Rent.STATUS_CHANGE_VERB[s]))

        if self.status in (Rent.STATUS_PENDING[0], Rent.STATUS_APPROVED[0]):
            s = Rent.STATUS_CANCELLED[0]
            available_statuses.append((s, Rent.STATUS_CHANGE_VERB[s]))

        return available_statuses


class RentHistory(TimeStampedModel):
    user = models.ForeignKey(JhUser, on_delete=models.PROTECT)
    new_status = models.CharField(verbose_name=_("Status"), choices=Rent.STATUS_CHOICES, max_length=20, null=True)
    new_renter = models.ForeignKey(JhUser,
                                   on_delete=models.PROTECT,
                                   related_name="+",
                                   verbose_name=_("New renter"),
                                   null=True)
    added_game = models.ForeignKey(GamePiece,
                                   on_delete=models.PROTECT,
                                   related_name="+",
                                   verbose_name=_("New game piece"),
                                   null=True)
    deleted_game = models.ForeignKey(GamePiece,
                                     on_delete=models.PROTECT,
                                     related_name="+",
                                     verbose_name=_("Deleted game piece"),
                                     null=True)
    edited_date_from = models.DateTimeField(verbose_name=_("Edited from"), null=True)
    edited_date_to = models.DateTimeField(verbose_name=_("Edited to"), null=True)
    rent = models.ForeignKey(Rent, on_delete=models.PROTECT, related_name='histories')


class Comment(TimeStampedModel):
    rent = models.ForeignKey(Rent, on_delete=models.PROTECT, related_name="comments")
    user = models.ForeignKey(JhUser, on_delete=models.PROTECT)
    message = models.TextField(verbose_name=_("Message"))
