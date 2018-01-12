from django.contrib import admin
from .models import GameGroup, GamePiece, InventoryItem


admin.site.register(GameGroup)
admin.site.register(GamePiece)
admin.site.register(InventoryItem)
