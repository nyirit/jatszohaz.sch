from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)

    def __str__(self):
        return self.user


class GameGroup(TimeStampedModel):
    name = models.TextField(verbose_name=_("Name"), blank=False)
    description = models.TextField(verbose_name=_("Description"), blank=False)
    image = models.ImageField(verbose_name=("Image"), default='/default.png')  # this doesn't work

    def __str__(self):
        return self.name


class GamePiece(TimeStampedModel):
    owner = models.OneToOneField(
        Profile,
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
        return self.game_group + self.notes


class GamePack(TimeStampedModel):
    name = models.TextField(verbose_name=_("Name"))
    games = models.ManyToManyField(GameGroup, related_name="packs")
    creator = models.ForeignKey(Profile, on_delete=models.PROTECT)
    active = models.BooleanField(verbose_name=_("Active"), default=False)

    def __str__(self):
        return self.name


class InventoryItem(TimeStampedModel):
    user = models.ForeignKey(Profile, on_delete=models.PROTECT)
    game = models.ForeignKey(GamePiece, on_delete=models.CASCADE)
    playable = models.BooleanField(verbose_name=_("Playable"), null=False, blank=False)
    missing_items = models.TextField(verbose_name=_("Missing items"))


class Rent(TimeStampedModel):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_GAVE_OUT = "gaveout"
    STATUS_BACK = "back"
    STATUS_DECLINED = "declined"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = (
        (STATUS_PENDING, _("Pending")),
        (STATUS_APPROVED, _("Approved")),
        (STATUS_GAVE_OUT, _("Gave out")),
        (STATUS_BACK, _("Brought back")),
        (STATUS_DECLINED, _("Declined")),
        (STATUS_CANCELLED, _("Cancelled"))
    )

    renter = models.ForeignKey(Profile, on_delete=models.PROTECT)
    games = models.ManyToManyField(GamePiece, verbose_name=_("Games"), related_name=_("rents"))
    date_from = models.DateTimeField(verbose_name=_("From"), blank=False, null=False)
    date_to = models.DateTimeField(verbose_name=_("To"), blank=False, null=False)
    status = models.IntegerField(verbose_name=_("Status"), choices=STATUS_CHOICES, default=STATUS_PENDING)
    bail = models.TextField(verbose_name=_("Bail"))


class RentActions(TimeStampedModel):
    user = models.ForeignKey(Profile, on_delete=models.PROTECT)
    new_status = models.IntegerField(verbose_name=_("Status"), choices=Rent.STATUS_CHOICES, null=False)
    rent = models.ForeignKey(Rent, on_delete=models.PROTECT)


class Comment(TimeStampedModel):
    rent = models.ForeignKey(Rent, on_delete=models.PROTECT)
    user = models.ForeignKey(Profile, on_delete=models.PROTECT)
    message = models.TextField(verbose_name=_("Message"))
