from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, CreateView

from jatszohaz.utils import DefaultUpdateView

from .models import News


class NewsPermissionRequiredMixin(PermissionRequiredMixin):
    """Base view for checking permissions."""
    permission_required = 'news.manage_news'


class NewsView(ListView):
    """Displaying news publicly."""
    model = News
    template_name = 'news.html'
    paginate_by = 5

    def get_queryset(self):
        queryset = News.objects

        if self.request.user.has_perm('news.manage_news'):
            return queryset.order_by('-created').all()

        return queryset.filter(published=True).order_by('-created').all()


class CreateNewsView(SuccessMessageMixin, NewsPermissionRequiredMixin, CreateView):
    """Admin view for creating new news objects."""
    model = News
    template_name = "default_update.html"
    fields = ['title', 'content', 'image', 'published']
    success_url = reverse_lazy('news:news')
    success_message = _("News created!")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['title'] = _("Create news")
        return data

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)


class EditNewsEntryView(SuccessMessageMixin, NewsPermissionRequiredMixin, DefaultUpdateView):
    """Admin view for editing existing news objects."""
    model = News
    fields = ['title', 'content', 'image', 'published']
    success_url = reverse_lazy('news:news')
    success_message = _("Entry edited!")
    title = _("Edit entry")
