from django.contrib import admin
from .models import Rent, Comment, RentHistory

admin.site.register(Rent)
admin.site.register(RentHistory)
admin.site.register(Comment)
