from django.contrib import admin
from .models import GameGroup, GamePiece, GamePack, InventoryItem


admin.site.register(GameGroup)
admin.site.register(GamePiece)
admin.site.register(GamePack)
admin.site.register(InventoryItem)
