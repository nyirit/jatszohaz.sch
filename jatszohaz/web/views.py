import logging
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import SuspiciousOperation
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, FormView, View

from braces.views import SuperuserRequiredMixin
from formtools.wizard.views import SessionWizardView

from .forms import JhUserForm, RentFormStep1, RentFormStep2, RentFormStep3, NewCommentForm, EditRentForm, AddGameForm
from .models import GameGroup, JhUser, Rent, Comment, GamePiece

logger = logging.getLogger(__name__)


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


class NewRentView(LoginRequiredMixin, SessionWizardView):
    template_name = "new_rent.html"
    form_list = [RentFormStep1, RentFormStep2, RentFormStep3]

    # https://chriskief.com/2013/05/24/django-form-wizard-and-getting-data-from-previous-steps/
    def get_form_initial(self, step):
        data = {}

        step0_data = self.storage.get_step_data('0')
        if step0_data is not None:
            data['date_from'] = step0_data['0-date_from']
            data['date_to'] = step0_data['0-date_to']

        step1_data = self.storage.get_step_data('1')
        if step1_data is not None:
            data['game_groups'] = step1_data['1-game_groups']

        return self.initial_dict.get(step, data)

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
        for gg_id in game_groups:
            gg = GameGroup.objects.get(id=gg_id)
            rent.games.add(gg.get_game_piece(date_from, date_to))
        rent.save()
        Comment.objects.create(
            rent=rent,
            user=user,
            message=comment
        ).save()

        messages.success(self.request, _("Successfully rented!"))
        return redirect(reverse_lazy('rent', kwargs={"pk": rent.pk}))


class MyRentsView(LoginRequiredMixin, ListView):
    model = Rent
    template_name = "my-rents.html"
    ordering = ['-created']

    def get_queryset(self):
        return self.request.user.rents.all()


class RentsView(PermissionRequiredMixin, ListView):
    model = Rent
    template_name = "rents.html"
    permission_required = 'web.manage_rents'
    ordering = ['-created']


class RentView(LoginRequiredMixin, DetailView):
    model = Rent
    template_name = "rent_detail.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['comment_form'] = NewCommentForm()
        context_data['rent_form'] = EditRentForm(instance=self.object)
        context_data['add_game_form'] = AddGameForm(date_from=self.object.date_from, date_to=self.object.date_to)
        return context_data


class NewCommentView(LoginRequiredMixin, FormView):
    form_class = NewCommentForm

    def get_object(self):
        return get_object_or_404(Rent, pk=self.kwargs['rent_pk'])

    def get(self, request, *args, **kwargs):
        return redirect(self.get_object().get_absolute_url())

    def form_valid(self, form):
        rent = self.get_object()
        user = self.request.user
        message = form.cleaned_data['comment']

        if rent.renter == user or user.has_perm('web.manage_rents'):
            Comment.objects.create(rent=rent, user=user, message=message).save()
            # TODO email notification
            messages.success(self.request, _("Successfully sent!"))
        else:
            raise SuspiciousOperation("No permissions for comment this rent!")

        return redirect(rent.get_absolute_url())


class EditRentView(PermissionRequiredMixin, UpdateView):
    model = Rent
    form_class = EditRentForm
    permission_required = 'web.manage_rents'
    raise_exception = True

    def get(self, request, *args, **kwargs):
        return redirect(self.get_object().get_absolute_url())

    def form_valid(self, form):
        # TODO email notification with form.changed_data
        messages.success(self.request, _("Rent changed!"))
        return super().form_valid(form)

    def form_invalid(self, form):
        # TODO show field errors in displayed page
        messages.error(self.request, _("Invalid form."))
        return redirect(self.get_object().get_absolute_url())

    def get_success_url(self):
        return self.get_object().get_absolute_url()


class ChangeRentStatusView(PermissionRequiredMixin, View):
    http_method_names = ['get', ]
    permission_required = 'web.manage_rents'
    raise_exception = True

    def get(self, request, *args, **kwargs):
        rent = get_object_or_404(Rent, pk=kwargs.get('rent_pk'))
        rent.status = kwargs.get('status')
        rent.save()
        rent.create_new_history(self.request.user)
        return redirect(rent.get_absolute_url())


class AddGameView(PermissionRequiredMixin, FormView):
    permission_required = 'web.manage_rents'
    raise_exception = True
    form_class = AddGameForm

    def get_rent(self):
        return get_object_or_404(Rent, pk=self.kwargs.get('rent_pk'))

    def form_valid(self, form):
        rent = self.get_rent()
        game = get_object_or_404(GamePiece, pk=form.cleaned_data['game'])
        if game.is_free(rent.date_from, rent.date_to):
            rent.games.add(game)
            messages.success(self.request, _("Game added."))
        else:
            messages.error(self.request, _("Game is already rented for this time."))

        return redirect(rent.get_absolute_url())

    def form_invalid(self, form):
        messages.error(self.request, _("Invalid form."))
        return redirect(self.get_rent().get_absolute_url())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        rent = self.get_rent()
        kwargs.update({'date_from': rent.date_from, 'date_to': rent.date_to})
        return kwargs


class RemoveGameView(PermissionRequiredMixin, View):
    http_method_names = ['get', ]
    permission_required = 'web.manage_rents'
    raise_exception = True

    def get(self, request, *args, **kwargs):
        rent = get_object_or_404(Rent, pk=kwargs.get('rent_pk'))
        game_piece = get_object_or_404(GamePiece, pk=kwargs.get('game_pk'))
        rent.games.remove(game_piece)
        rent.save()
        return redirect(rent.get_absolute_url())
