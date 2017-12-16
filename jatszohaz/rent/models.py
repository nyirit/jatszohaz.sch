from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel
from inventory.models import GamePiece
from jatszohaz.models import JhUser


class Rent(TimeStampedModel):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_GAVE_OUT = "gaveout"
    STATUS_IN_MY_ROOM = "inmyroom"
    STATUS_BACK = "back"
    STATUS_DECLINED = "declined"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = (
        (STATUS_PENDING, _("Pending")),
        (STATUS_APPROVED, _("Approved")),
        (STATUS_GAVE_OUT, _("Gave out")),
        (STATUS_IN_MY_ROOM, _("In my room")),
        (STATUS_BACK, _("Brought back")),
        (STATUS_DECLINED, _("Declined")),
        (STATUS_CANCELLED, _("Cancelled"))
    )

    renter = models.ForeignKey(JhUser, on_delete=models.PROTECT, related_name="rents")
    games = models.ManyToManyField(GamePiece, verbose_name=_("Games"), related_name="rents")
    date_from = models.DateTimeField(verbose_name=_("From"), blank=False, null=False)
    date_to = models.DateTimeField(verbose_name=_("To"), blank=False, null=False)
    status = models.CharField(verbose_name=_("Status"), choices=STATUS_CHOICES, default=STATUS_PENDING, max_length=20)
    bail = models.CharField(verbose_name=_("Bail"), max_length=30, blank=True)

    def __str__(self):
        return "%s (%s - %s)" % (self.renter.full_name2(), self.date_from, self.date_to)

    class Meta:
        permissions = (
            ('manage_rents', _('Manage rents')),
            ('view_stat', _('View rent statistics')),
        )

    def get_absolute_url(self):
        return reverse("rent:details", kwargs={'pk': self.pk})

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
