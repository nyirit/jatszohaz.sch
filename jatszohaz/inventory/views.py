import logging
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, ListView, UpdateView, FormView
from inventory.forms import GameForm

from .models import InventoryItem, GamePiece, GamePack

logger = logging.getLogger(__name__)


class InventoryPermissionRequiredMixin(PermissionRequiredMixin):
    permission_required = 'manage_inventory'


class NewInvView(SuccessMessageMixin, InventoryPermissionRequiredMixin, CreateView):
    model = InventoryItem
    fields = ['game', 'playable', 'missing_items', ]
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
    model = GamePiece
    template_name = "inventory/list-inventory.html"


class InvListGameView(InventoryPermissionRequiredMixin, ListView):
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
    model = InventoryItem
    fields = ['user', 'game', 'playable', 'missing_items', ]
    template_name = "inventory/edit-inventory.html"
    success_url = reverse_lazy('inventory:list')


class NewGameWithGroupView(InventoryPermissionRequiredMixin, FormView):
    model = GamePiece
    template_name = "inventory/new_game.html"
    form_class = GameForm

    def form_valid(self, form):
        form.save()
        owner = form.cleaned_data['owner']
        notes = form.cleaned_data['notes']
        priority = form.cleaned_data['priority']
        GamePiece.objects.create(game_group=form.instance, owner=owner, notes=notes, priority=priority).save()
        messages.success(self.request, "Successfully created game and gamegroup!")
        return HttpResponseRedirect("")


class NewGameView(InventoryPermissionRequiredMixin, CreateView):
    model = GamePiece
    template_name = "inventory/new_game.html"
    fields = ['owner', 'game_group', 'notes', 'priority']
    success_url = reverse_lazy('inventory:list')


class GamePackView(InventoryPermissionRequiredMixin, ListView):
    model = GamePack
    template_name = "inventory/list-gamepack.html"


class NewGamePackView(SuccessMessageMixin, InventoryPermissionRequiredMixin, CreateView):
    model = GamePack
    fields = ['name', 'games', 'active', ]
    template_name = "inventory/new_gamepack.html"
    success_url = reverse_lazy("inventory:gamepacks")
    success_message = _("Game pack successfully created.")

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)


class EditGamePackView(SuccessMessageMixin, InventoryPermissionRequiredMixin, UpdateView):
    model = GamePack
    fields = ['name', 'games', 'active', ]
    template_name = "inventory/edit-gamepack.html"
    success_url = reverse_lazy("inventory:gamepacks")
    success_message = _("Game pack successfully edited.")