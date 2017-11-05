from django.views.generic import TemplateView, ListView, UpdateView, RedirectView
from web.models import GameGroup, JhUser


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data()
        if not self.request.user.is_anonymous:
            ctx['username'] = self.request.user.full_name2()
        return ctx

class GamesView(ListView):
    model = GameGroup
    template_name = "games.html"

class MyProfileView(UpdateView):
    model = JhUser
    template_name = "profile.html"
    fields = ["user", ]

    def get_object(self, queryset=None):
        return self.request.user;

class ProfileView(UpdateView):
    model = JhUser
    template_name = "profile.html"