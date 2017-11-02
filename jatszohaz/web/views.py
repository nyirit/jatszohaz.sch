from django.views.generic import TemplateView, ListView, UpdateView
from web.models import GameGroup, Profile


class HomeView(TemplateView):
    template_name = "home.html"

class GamesView(ListView):
    model = GameGroup
    template_name = "games.html"

class MyProfileView(UpdateView):
    model = Profile
    template_name = "profile.html"
    fields = ["user", ]

    def get_object(self, queryset=None):
        return self.request.user;

class ProfileView(UpdateView):
    model = Profile
    template_name = "profile.html"
