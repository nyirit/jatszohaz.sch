import logging
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, ListView, UpdateView
from .models import InventoryItem, GamePiece

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
    template_name = "inventory/list.html"


class EditView(InventoryPermissionRequiredMixin, UpdateView):
    model = InventoryItem
    fields = ['user', 'game', 'playable', 'missing_items', ]
    template_name = "inventory/edit.html"
    success_url = reverse_lazy('inventory:list')
