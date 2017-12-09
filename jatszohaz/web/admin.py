from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    JhUser, GameGroup, GamePiece, GamePack, InventoryItem, Rent, RentActions, Comment)


class JhUserAdmin(UserAdmin):
    readonly_fields = ('username', 'first_name', 'last_name', 'date_joined', 'last_login', )


admin.site.register(JhUser, JhUserAdmin)
admin.site.register(GameGroup)
admin.site.register(GamePiece)
admin.site.register(GamePack)
admin.site.register(InventoryItem)
admin.site.register(Rent)
admin.site.register(RentActions)
admin.site.register(Comment)
