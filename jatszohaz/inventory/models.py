import logging
from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel
from jatszohaz.models import JhUser

logger = logging.getLogger(__name__)


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
        from rent.models import Rent
        return self.rents\
            .exclude(status__in=[Rent.STATUS_CANCELLED, Rent.STATUS_DECLINED])\
            .filter(models.Q(date_from__range=(date_from, date_to)) | models.Q(date_to__range=(date_from, date_to)))\
            .count() == 0

    def get_latest_inventory_item(self):
        return self.inventories.last()

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
    game = models.ForeignKey(GamePiece, on_delete=models.CASCADE, related_name="inventories")
    playable = models.BooleanField(verbose_name=_("Playable"), null=False, blank=False)
    missing_items = models.CharField(verbose_name=_("Missing items"), max_length=100, blank=True)

    class Meta:
        permissions = (
            ('manage_inventory', _('Manage Inventory')),
        )
