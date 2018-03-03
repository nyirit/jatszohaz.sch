from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import JhUser


class JhUserAdmin(UserAdmin):
    readonly_fields = ('username', 'first_name', 'last_name', 'date_joined', 'last_login', )


JhUserAdmin.fieldsets += ('Custom fields', {'fields': ('room', 'mobile', 'checked_profile')}),
admin.site.register(JhUser, JhUserAdmin)
