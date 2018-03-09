from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView

from .models import News


class NewsPermissionRequiredMixin(PermissionRequiredMixin):
    permission_required = 'news.manage_news'


class NewsView(ListView):
    model = News
    template_name = 'news.html'
    paginate_by = 5

    def get_queryset(self):
        queryset = News.objects

        if self.request.user.has_perm('news.manage_news'):
            return queryset.order_by('-created').all()

        return queryset.filter(published=True).order_by('-created').all()


class CreateNewsView(SuccessMessageMixin, NewsPermissionRequiredMixin, CreateView):
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


class EditNewsEntryView(SuccessMessageMixin, NewsPermissionRequiredMixin, UpdateView):
    model = News
    template_name = "default_update.html"
    fields = ['title', 'content', 'image', 'published']
    success_url = reverse_lazy('news:news')
    success_message = _("Entry edited!")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['title'] = _("Edit entry")
        return data
