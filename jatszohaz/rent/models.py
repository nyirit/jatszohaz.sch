from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel
from inventory.models import GamePiece
from jatszohaz.models import JhUser


class Rent(TimeStampedModel):
    STATUS_PENDING = ("pending", _("Pending"))
    STATUS_APPROVED = ("approved", _("Approved"))
    STATUS_GAVE_OUT = ("gaveout", _("Gave out"))
    STATUS_IN_MY_ROOM = ("inmyroom", _("In my room"))
    STATUS_BACK = ("back", _("Brought back"))
    STATUS_DECLINED = ("declined", _("Declined"))
    STATUS_CANCELLED = ("cancelled", _("Cancelled"))
    STATUS_CHOICES = (
        STATUS_PENDING,
        STATUS_APPROVED,
        STATUS_GAVE_OUT,
        STATUS_IN_MY_ROOM,
        STATUS_BACK,
        STATUS_DECLINED,
        STATUS_CANCELLED
    )

    renter = models.ForeignKey(JhUser, on_delete=models.PROTECT, related_name="rents")
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

    def create_new_history(self, user):
        RentHistory.objects.create(user=user, new_status=self.status, rent=self)


class RentHistory(TimeStampedModel):
    user = models.ForeignKey(JhUser, on_delete=models.PROTECT)
    new_status = models.CharField(verbose_name=_("Status"), choices=Rent.STATUS_CHOICES, max_length=20)
    rent = models.ForeignKey(Rent, on_delete=models.PROTECT, related_name='histories')


class Comment(TimeStampedModel):
    rent = models.ForeignKey(Rent, on_delete=models.PROTECT, related_name="comments")
    user = models.ForeignKey(JhUser, on_delete=models.PROTECT)
    message = models.TextField(verbose_name=_("Message"))
