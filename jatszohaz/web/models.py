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
    mobile = models.CharField(
        verbose_name=_('mobile'),
        max_length=100,
        help_text=_('Mobile number for helping communication if necessery.'),
        blank=True
    )
    room = models.CharField(
        verbose_name=_('room'),
        max_length=100,
        help_text=_('Room number.'),
        blank=True
    )

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
        if self.has_social_auth():
            for i in self.social_auth.first().extra_data['eduPersonEntitlement']:
                if i['id'] == settings.EDU_PERSON_ENTITLEMENT_ID:
                    return i

    def has_social_auth(self):
        return self.social_auth.count() > 0

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
    name = models.CharField(verbose_name=_("Name"), blank=False, unique=True, max_length=100)
    description = models.TextField(verbose_name=_("Description"), blank=False)
    short_description = models.CharField(verbose_name=_("Short Description"), blank=False, max_length=100)
    image = models.ImageField(verbose_name="Image")

    def get_game_piece(self, date_from, date_to):
        for piece in self.game_pieces.order_by('-priority'):
            if piece.is_free(date_from, date_to):
                return piece
        raise GameGroup.DoesNotExist("No free piece available!")

    def has_free_piece(self, date_from, date_to):
        for piece in self.game_pieces.order_by('-priority'):
            if piece.is_free(date_from, date_to):
                return True
        return False

    def __str__(self):
        return '%s' % (self.name)


class GamePiece(TimeStampedModel):
    owner = models.ForeignKey(
        JhUser,
        on_delete=models.PROTECT,  # do not delete users, who owns a game
        verbose_name=_("Owner"),
        null=True,
        blank=True
    )
    game_group = models.ForeignKey(GameGroup, on_delete=models.CASCADE, related_name='game_pieces')
    notes = models.CharField(verbose_name=_("Notes"), max_length=100)
    # Priority: which GamePiece should be rented first from same GameGroup.
    # Higher number will be rented first.
    priority = models.PositiveSmallIntegerField(verbose_name="Priority", default=0)

    def is_free(self, date_from, date_to):
        return self.rents\
            .exclude(status__in=[Rent.STATUS_CANCELLED, Rent.STATUS_DECLINED])\
            .filter(models.Q(date_from__range=(date_from, date_to)) | models.Q(date_to__range=(date_from, date_to)))\
            .count() == 0

    def __str__(self):
        return '%s - %s' % (self.game_group, self.notes)


class GamePack(TimeStampedModel):
    name = models.CharField(verbose_name=_("Name"), max_length=100, unique=True)
    games = models.ManyToManyField(GameGroup, related_name="packs")
    creator = models.ForeignKey(JhUser, on_delete=models.PROTECT)
    active = models.BooleanField(verbose_name=_("Active"), default=False)

    def __str__(self):
        return '%s' % (self.name)


class InventoryItem(TimeStampedModel):
    user = models.ForeignKey(JhUser, on_delete=models.PROTECT)
    game = models.ForeignKey(GamePiece, on_delete=models.CASCADE)
    playable = models.BooleanField(verbose_name=_("Playable"), null=False, blank=False)
    missing_items = models.CharField(verbose_name=_("Missing items"), max_length=100)


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


class RentActions(TimeStampedModel):
    user = models.ForeignKey(JhUser, on_delete=models.PROTECT)
    new_status = models.CharField(verbose_name=_("Status"), choices=Rent.STATUS_CHOICES, max_length=20)
    rent = models.ForeignKey(Rent, on_delete=models.PROTECT)


class Comment(TimeStampedModel):
    rent = models.ForeignKey(Rent, on_delete=models.PROTECT)
    user = models.ForeignKey(JhUser, on_delete=models.PROTECT)
    message = models.TextField(verbose_name=_("Message"))
