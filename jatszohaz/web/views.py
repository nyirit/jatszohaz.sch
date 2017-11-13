from django.views.generic import TemplateView, ListView, DetailView
from web.models import GameGroup, JhUser


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data()
        if not self.request.user.is_anonymous:
            ctx['username'] = self.request.user.full_name2()
        return ctx


class CalendarView(TemplateView):
    template_name = "calendar.html"


class GamesView(ListView):
    model = GameGroup
    template_name = "games.html"


class MyProfileView(DetailView):
    model = JhUser
    template_name = "profile.html"

    def get_object(self, queryset=None):
        return self.request.user


class ProfileView(DetailView):
    model = JhUser
    template_name = "profile.html"
