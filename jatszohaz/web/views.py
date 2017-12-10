from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, ListView, DetailView, UpdateView

from braces.views import SuperuserRequiredMixin
from formtools.wizard.views import SessionWizardView

from .forms import JhUserForm, RentFormStep1, RentFormStep2, RentFormStep3
from .models import GameGroup, JhUser, Rent, Comment


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


class MyProfileView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = JhUser
    success_url = reverse_lazy('my-profile')
    success_message = _("Successfully updated!")
    form_class = JhUserForm
    template_name = "profile.html"

    def get_object(self, queryset=None):
        return self.request.user


class ProfileView(SuperuserRequiredMixin, DetailView):
    # TODO permission check
    model = JhUser
    template_name = "profile_detail.html"


class RentView(LoginRequiredMixin, SessionWizardView):
    template_name = "rent.html"
    form_list = [RentFormStep1, RentFormStep2, RentFormStep3]

    def done(self, form_list, **kwargs):
        forms = list(form_list)
        step0_data = forms[0].cleaned_data
        step1_data = forms[1].cleaned_data
        step2_data = forms[2].cleaned_data
        date_from = step0_data['date_from']
        date_to = step0_data['date_to']
        game_groups = step1_data['game_groups']
        comment = step2_data['comment']

        user = self.request.user
        rent = Rent.objects.create(
            renter=user,
            date_from=date_from,
            date_to=date_to
        )
        for gg in game_groups:
            rent.games.add(gg.get_game_piece(date_from, date_to))
        rent.save()
        Comment.objects.create(
            rent=rent,
            user=user,
            message=comment
        ).save()

        messages.success(self.request, _("Successfully rented!"))
        return redirect(reverse_lazy('rent'))  # TODO open specific Rent instance
