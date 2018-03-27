import logging
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_resized import ResizedImageField
from model_utils.models import TimeStampedModel
from jatszohaz.models import JhUser

logger = logging.getLogger(__name__)


class GameGroup(TimeStampedModel):
    name = models.CharField(verbose_name=_("Name"), blank=False, unique=True, max_length=100)
    description = models.TextField(verbose_name=_("Description"), blank=False)
    short_description = models.CharField(verbose_name=_("Short Description"), blank=False, max_length=100)
    image = ResizedImageField(size=[130, 100], crop=['middle', 'center'], verbose_name="Image")
    players = models.CharField(verbose_name=_("Players"), max_length=100)
    playtime = models.CharField(verbose_name=_("Playing time"), max_length=100)
    base_game = models.ForeignKey("self",
                                  on_delete=models.SET_NULL,
                                  verbose_name=_("Base game"),
                                  help_text=_("Game needed to play this one."),
                                  blank=True,
                                  null=True)

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
    notes = models.CharField(verbose_name=_("Notes"), max_length=100, blank=True)
    # Priority: which GamePiece should be rented first from same GameGroup.
    # Higher number will be rented first.
    priority = models.PositiveSmallIntegerField(verbose_name=_("Priority"), default=0)
    rentable = models.BooleanField(verbose_name=_("Rentable"), null=False, blank=False, default=True)
    buying_date = models.DateField(verbose_name=_("Buying date"), null=True, blank=True)
    place = models.CharField(verbose_name=_("Place"), max_length=20, blank=True)
    price = models.IntegerField(verbose_name=_("Price (Ft)"), validators=[MinValueValidator(0)], default=0)

    def is_free(self, date_from, date_to):
        from rent.models import Rent

        last_inv = self.get_latest_inventory_item()

        return (self.rentable and (last_inv is None or last_inv.playable) and
                self.rents
                .exclude(status__in=[Rent.STATUS_CANCELLED, Rent.STATUS_DECLINED])
                .filter(models.Q(date_from__range=(date_from, date_to)) | models.Q(date_to__range=(date_from, date_to)))
                .count() == 0)

    def get_latest_inventory_item(self):
        return self.inventories.last()

    def __str__(self):
        return '%s - %s' % (self.game_group, self.notes)


class InventoryItem(TimeStampedModel):
    user = models.ForeignKey(JhUser, on_delete=models.PROTECT)
    game = models.ForeignKey(GamePiece, on_delete=models.CASCADE, related_name="inventories")
    playable = models.BooleanField(verbose_name=_("Playable"), null=False, blank=False)
    missing_items = models.CharField(verbose_name=_("Missing items"), max_length=100, blank=True)
    rules = models.CharField(verbose_name=_("Rules"), max_length=100, default='-')

    class Meta:
        permissions = (
            ('manage_inventory', _('Manage Inventory')),
        )
