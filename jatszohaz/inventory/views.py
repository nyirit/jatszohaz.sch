import logging
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, ListView, UpdateView, FormView
from inventory.forms import GameForm, GamePieceForm

from .models import InventoryItem, GamePiece, GameGroup
from jatszohaz.utils import DefaultUpdateView

logger = logging.getLogger(__name__)


class InventoryPermissionRequiredMixin(PermissionRequiredMixin):
    """Base view for checking permissions."""
    permission_required = 'inventory.manage_inventory'


class NewInvView(SuccessMessageMixin, InventoryPermissionRequiredMixin, CreateView):
    """View for creating a new inventory."""
    model = InventoryItem
    fields = ['game', 'playable', 'missing_items', 'rules', ]
    template_name = "inventory/new_inventory.html"
    success_url = reverse_lazy('inventory:list')
    success_message = _("Inventory created")

    def get_initial(self):
        initial = super().get_initial()
        initial['game'] = self.kwargs.get('game_pk', '')
        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class InvListView(InventoryPermissionRequiredMixin, ListView):
    """View for listing all the existing inventories."""
    model = GamePiece
    template_name = "inventory/list-inventory.html"
    ordering = "game_group__name"


class InvListGameView(InventoryPermissionRequiredMixin, ListView):
    """View for listing all existing inventories for a given physical game."""
    model = InventoryItem
    template_name = "inventory/list_game.html"

    def get_game(self):
        return get_object_or_404(GamePiece, pk=self.kwargs['game_pk'])

    def get_queryset(self):
        return InventoryItem.objects.filter(game=self.get_game()).order_by("-created")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = self.get_game()
        context['game_piece'] = game
        context['rent_history'] = game.rents.order_by("-date_from").all()
        return context


class EditView(InventoryPermissionRequiredMixin, UpdateView):
    """Editing an existing inventory object."""
    model = InventoryItem
    fields = ['user', 'game', 'playable', 'missing_items', ]
    template_name = "inventory/edit-inventory.html"
    success_url = reverse_lazy('inventory:list')


class NewGameWithGroupView(InventoryPermissionRequiredMixin, FormView):
    """Creating a new GameGroup and connected GamePiece objects."""
    model = GamePiece
    template_name = "inventory/new_game.html"
    form_class = GameForm

    def form_valid(self, form):
        form.save()
        data = dict(
            owner=form.cleaned_data['owner'],
            notes=form.cleaned_data['notes'],
            priority=form.cleaned_data['priority'],
            rentable=form.cleaned_data['rentable'],
            buying_date=form.cleaned_data['buying_date'],
            place=form.cleaned_data['place'],
            price=form.cleaned_data['price'],

        )
        GamePiece.objects.create(game_group=form.instance, **data).save()
        messages.success(self.request, "Successfully created game and gamegroup!")
        return HttpResponseRedirect(reverse_lazy('inventory:new-game-with-group'))


class NewGameView(InventoryPermissionRequiredMixin, CreateView):
    """Creating a name GamePiece object connected to an already existing GameGroup."""
    model = GamePiece
    form_class = GamePieceForm
    template_name = "inventory/new_game.html"
    success_url = reverse_lazy('inventory:list')


class EditGameGroup(SuccessMessageMixin, InventoryPermissionRequiredMixin, DefaultUpdateView):
    """View for editing an existing GameGroup object."""
    model = GameGroup
    fields = ['name', 'description', 'short_description', 'base_game', 'min_players', 'max_players',
              'playtime', 'playtime_category', 'hide']
    success_url = reverse_lazy("inventory:list")
    success_message = _("Game group successfully edited.")
    title = _("Edit game group")


class EditGamePiece(SuccessMessageMixin, InventoryPermissionRequiredMixin, DefaultUpdateView):
    """View for editing an existing GamePiece object."""
    model = GamePiece
    form_class = GamePieceForm
    success_url = reverse_lazy("inventory:list")
    success_message = _("Game group successfully edited.")
    title = _("Edit game piece")
