import logging
from django.contrib.auth import user_logged_in
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel

logger = logging.getLogger(__name__)


class JhUser(AbstractUser):
    def get_entitlements(self):
        """
        Gets all auth.sch group memberships.
        Map keys:
         - title (list): all titles in VIR
         - status (str): öregtag tag or körvezető
         - start (date): join date
         - end (date): leave date
        :return: data map of the specified group.
        """
        for i in self.social_auth.first().extra_data['eduPersonEntitlement']:
            if i['id'] == settings.EDU_PERSON_ENTITLEMENT_ID:
                return i

    @receiver(user_logged_in)
    def user_logged_in(sender, user, request, **kwargs):
        user.update_permissions()

    def update_permissions(self):
        """
        Update user rights according to its entitlements
        """
        if self.get_entitlements() is not None:
            # TODO chage superuser status to actual permissions
            self.is_staff = True
            self.is_superuser = True
            self.save()
            logger.info("Updated permissions for user %d." % self.pk)

    def full_name(self):
        """
        :return: First name + lLst name
        """
        return "%s %s" % (self.first_name, self.last_name)

    def full_name2(self):
        """
        :return: Last name + First name
        """
        return "%s %s" % (self.last_name, self.first_name)

    def __str__(self):
        return "%s - %s" % (self.full_name2(), self.email)


class GameGroup(TimeStampedModel):
    name = models.TextField(verbose_name=_("Name"), blank=False)
    description = models.TextField(verbose_name=_("Description"), blank=False)
    short_description = models.TextField(verbose_name=_("Short Description"), blank=False)
    image = models.ImageField(verbose_name="Image")

    def __str__(self):
        return '%s' % (self.name)


class GamePiece(TimeStampedModel):
    owner = models.OneToOneField(
        JhUser,
        on_delete=models.PROTECT,  # do not delete users, who owns a game
        verbose_name=_("Owner"),
        null=True,
        blank=True
    )
    game_group = models.ForeignKey(GameGroup, on_delete=models.CASCADE)
    notes = models.TextField(verbose_name=_("Notes"))
    # Priority: which GamePiece should be rented first from same GameGroup.
    # Higher number will be rented first.
    priority = models.PositiveSmallIntegerField(verbose_name="Priority", default=0)

    def __str__(self):
        return '%s - %s' % (self.game_group, self.notes)


class GamePack(TimeStampedModel):
    name = models.TextField(verbose_name=_("Name"))
    games = models.ManyToManyField(GameGroup, related_name="packs")
    creator = models.ForeignKey(JhUser, on_delete=models.PROTECT)
    active = models.BooleanField(verbose_name=_("Active"), default=False)

    def __str__(self):
        return '%s' % (self.name)


class InventoryItem(TimeStampedModel):
    user = models.ForeignKey(JhUser, on_delete=models.PROTECT)
    game = models.ForeignKey(GamePiece, on_delete=models.CASCADE)
    playable = models.BooleanField(verbose_name=_("Playable"), null=False, blank=False)
    missing_items = models.TextField(verbose_name=_("Missing items"))


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

    renter = models.ForeignKey(JhUser, on_delete=models.PROTECT)
    games = models.ManyToManyField(GamePiece, verbose_name=_("Games"), related_name=_("rents"))
    date_from = models.DateTimeField(verbose_name=_("From"), blank=False, null=False)
    date_to = models.DateTimeField(verbose_name=_("To"), blank=False, null=False)
    status = models.TextField(verbose_name=_("Status"), choices=STATUS_CHOICES, default=STATUS_PENDING)
    bail = models.TextField(verbose_name=_("Bail"))

    class Meta:
        permissions = (
            ('manage_rents', _('Manage rents')),
            ('view_stat', _('View rent statistics')),
        )


class RentActions(TimeStampedModel):
    user = models.ForeignKey(JhUser, on_delete=models.PROTECT)
    new_status = models.TextField(verbose_name=_("Status"), choices=Rent.STATUS_CHOICES, null=False)
    rent = models.ForeignKey(Rent, on_delete=models.PROTECT)


class Comment(TimeStampedModel):
    rent = models.ForeignKey(Rent, on_delete=models.PROTECT)
    user = models.ForeignKey(JhUser, on_delete=models.PROTECT)
    message = models.TextField(verbose_name=_("Message"))
