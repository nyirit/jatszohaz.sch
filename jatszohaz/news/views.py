from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView

from .models import News


class NewsPermissionRequiredMixin(PermissionRequiredMixin):
    permission_required = 'manage_news'


class NewsView(NewsPermissionRequiredMixin, ListView):
    model = News
    template_name = 'news.html'
