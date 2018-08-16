import logging
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from django_resized import ResizedImageField
from model_utils.models import TimeStampedModel
from jatszohaz.models import JhUser

logger = logging.getLogger(__name__)


class GameGroup(TimeStampedModel):
    LENGTH_SHORT = ("short", _("short (20 mins)"))
    LENGTH_MEDIUM = ("medium", _("medium (20-60 mins)"))
    LENGTH_LONG = ("long", _("long (60+ mins)"))
    LENGTH_CHOICES = (
        LENGTH_SHORT,
        LENGTH_MEDIUM,
        LENGTH_LONG
    )
    name = models.CharField(verbose_name=_("Name"), blank=False, unique=True, max_length=100)
    description = models.TextField(verbose_name=_("Description"), blank=False)
    short_description = models.CharField(verbose_name=_("Short Description"), blank=False, max_length=100)
    image = ResizedImageField(size=[130, 100], crop=['middle', 'center'], verbose_name="Image")
    min_players = models.IntegerField(verbose_name=_("Min. players"),
                                      help_text=_("How many players are needed to play"),
                                      validators=[MinValueValidator(1)],
                                      null=True)
    max_players = models.IntegerField(verbose_name=_("Max. players"), help_text=_("How many players can play at most"),
                                      validators=[MinValueValidator(1)],
                                      null=True)
    playtime = models.CharField(verbose_name=_("Playing time"),
                                help_text=_("Example: 20 mins (this is directly displayed to the user)"),
                                max_length=100)
    playtime_category = models.CharField(verbose_name=_("Playtime category"), choices=LENGTH_CHOICES, max_length=20)
    base_game = models.ForeignKey("self",
                                  on_delete=models.SET_NULL,
                                  verbose_name=_("Base game"),
                                  help_text=_("Game needed to play this one."),
                                  blank=True,
                                  null=True)
    hide = models.BooleanField(
        verbose_name=_("Hide from users"),
        help_text=_("If true isn't shown in Our games page."),
        blank=True,
        default=False
    )

    class Meta:
        ordering = ['name', ]

    def get_game_piece(self, date_from, date_to):
        for piece in self.game_pieces.order_by('priority'):
            if piece.is_free(date_from, date_to):
                return piece
        raise GameGroup.DoesNotExist("No free piece available!")

    def has_free_piece(self, date_from, date_to):
        for piece in self.game_pieces.all():
            if piece.is_free(date_from, date_to):
                return True
        return False

    @property
    def players(self):
        if self.min_players and self.max_players:
            if self.min_players == self.max_players:
                return self.min_players
            else:
                return "%d - %d" % (self.min_players, self.max_players)
        return None

    def __str__(self):
        return self.name


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
    # Lower number will be rented first.
    priority = models.PositiveSmallIntegerField(verbose_name=_("Priority"), default=0)
    rentable = models.BooleanField(verbose_name=_("Rentable"), null=False, blank=False, default=True)
    buying_date = models.DateField(verbose_name=_("Buying date"), null=True, blank=True)
    place = models.CharField(verbose_name=_("Place"), max_length=20, blank=True)
    price = models.IntegerField(verbose_name=_("Price (Ft)"), validators=[MinValueValidator(0)], default=0)

    class Meta:
        ordering = ['game_group__name', ]

    def is_free(self, date_from, date_to, ignored_rent_pk=None):
        from rent.models import Rent

        last_inv = self.get_latest_inventory_item()

        return (self.rentable and (last_inv is None or last_inv.playable) and
                self.rents
                .exclude(status__in=[Rent.STATUS_CANCELLED[0],
                                     Rent.STATUS_DECLINED[0], Rent.STATUS_BACK[0]])
                .exclude(pk=ignored_rent_pk)
                .filter(
                    models.Q(date_from__range=(date_from, date_to)) |
                    models.Q(date_from__lte=date_from, date_to__gte=date_from)
                )
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
        ordering = ['created', ]
        permissions = (
            ('manage_inventory', _('Manage Inventory')),
        )
