from datetime import datetime
import logging
from urllib.parse import urljoin
from django.conf import settings

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import SuspiciousOperation, PermissionDenied
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.dateparse import parse_date
from django.views.generic import ListView, DetailView, UpdateView, FormView, View, TemplateView
from formtools.wizard.views import SessionWizardView

from .forms import RentFormStep1, RentFormStep2, RentFormStep3, NewCommentForm, EditRentForm, AddGameForm
from inventory.models import GameGroup
from jatszohaz.utils import jh_send_mail, send_message_to_members
from .models import Rent, Comment, GamePiece


logger = logging.getLogger(__name__)


class NewView(LoginRequiredMixin, SessionWizardView):
    """
    View for creating a new rent.

    It contains multiple steps:
     1) Selecting dates
     2) Selecting games. Only games available during the given time period are shown.
     3) Add comment, finalize rent.

    There's a form corresponding to each step.
    """

    template_name = "rent/new_rent.html"
    form_list = [RentFormStep1, RentFormStep2, RentFormStep3]

    # https://chriskief.com/2013/05/24/django-form-wizard-and-getting-data-from-previous-steps/
    def get_form_initial(self, step):
        data = {}

        step0_data = self.storage.get_step_data('0')
        if step0_data is not None:
            # let's make sure we have dates instead of string representations,
            # because at later steps the cleaned_data will provide dates as well.
            data['date_from'] = parse_date(step0_data['0-date_from'])
            data['date_to'] = parse_date(step0_data['0-date_to'])

        step1_data = self.storage.get_step_data('1')
        if step1_data is not None:
            ids = dict(step1_data).get('1-game_groups', ())
            data['game_groups'] = GameGroup.objects.filter(id__in=ids).order_by("name").all()

        return self.initial_dict.get(step, data)

    def send_email(self, context):
        """Sends notification email to mailing list"""

        if not settings.NEW_RENT_EMAIL_NOTIFICATION:
            return

        recipient = settings.NOTIFICATION_EMAIL_TO
        if recipient:
            subject = _("%s new rent") % settings.EMAIL_SUBJECT_PREFIX
            message = _("Hi!<br/><br/>New rent created!<br/><br/>"
                        "Renter: %(renter)s<br/>"
                        "Dates: %(date_from)s - %(date_to)s<br/>"
                        "Games: %(games)s<br/>"
                        "Comment: %(comment)s<br/>"
                        "Details: <a href=\"%(url)s\">%(url)s<a><br/><br/>"
                        "Best wishes,<br/>Játszóház") % context

            try:
                jh_send_mail(subject, message, [recipient, ])
            except Exception as e:
                logger.error("Failed to send email! %s" % e)

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
            date_to=datetime.combine(date_to, datetime.max.time())
        )

        if user.has_perm('rent.manage_rents'):
            rent.status = Rent.STATUS_APPROVED[0]

        for gg_id in game_groups or ():
            gg = GameGroup.objects.get(id=gg_id)
            rent.games.add(gg.get_game_piece(date_from, date_to))
        rent.save()
        comment = Comment.objects.create(
            rent=rent,
            user=user,
            message=comment
        )

        if not rent.renter.has_perm('rent.manage_rents'):
            context = {
                'url': urljoin(settings.SITE_DOMAIN, str(rent.get_absolute_url())),
                'renter': rent.renter.full_name2(),
                'date_from': rent.date_from,
                'date_to': rent.date_to,
                'games': ', '.join([gp.game_group.name for gp in rent.games.all()]),
                'comment': comment.message
            }
            self.send_email(context)
            send_message_to_members('slack/new_rent.html', context)

        messages.success(self.request, _("Successfully rented!"))
        return redirect(rent.get_absolute_url())


class MyView(LoginRequiredMixin, ListView):
    """Showing Rent created by the logged in user."""

    model = Rent
    template_name = "rent/my_rents.html"
    ordering = ['-date_from']
    paginate_by = 10

    def get_queryset(self):
        self.queryset = self.request.user.rents
        return super().get_queryset()


class RentsView(PermissionRequiredMixin, ListView):
    """Showing all the rents for administrators."""

    model = Rent
    template_name = "rent/rents.html"
    permission_required = 'rent.manage_rents'
    paginate_by = 10

    def get_queryset(self):
        self.my_todo = Rent.objects.filter(histories__user=self.request.user).distinct().order_by('-created')\
                    .exclude(status__in=(Rent.STATUS_CANCELLED[0], Rent.STATUS_DECLINED[0], Rent.STATUS_BACK[0]))

        status = self.kwargs.get('status')

        result = Rent.objects.all().order_by('-created')
        if status is not None:
            if status == 'ToDo':
                result = self.my_todo
            else:
                result = result.filter(status=status)

        self.queryset = result

        return result

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)

        context['active_status'] = self.kwargs.get('status')
        context['statuses'] = list()
        status_count = Rent.get_count_by_status()
        sum_count = 0
        for status in Rent.STATUS_CHOICES:
            count = status_count[status[0]] if status_count.get(status[0]) is not None else 0
            context['statuses'].append(status + (count, ))
            sum_count += count

        context['sum_count'] = sum_count
        context['todo_count'] = self.my_todo.count()

        context['rent_pks'] = ','.join([str(r.pk) for r in self.queryset if r.status == Rent.STATUS_IN_MY_ROOM[0]])

        return context


class DetailsView(LoginRequiredMixin, DetailView):
    """
    Showing details of one rent object.

    Permission is only granted if the user is an administrator or the owner/creator of the rent object.
    """

    model = Rent
    template_name = "rent/rent_detail.html"

    def dispatch(self, request, *args, **kwargs):
        result = super().dispatch(request, *args, **kwargs)

        # Handling permission
        user = request.user
        if user.is_authenticated and not (user.has_perm('rent.manage_rents') or user == self.get_object().renter):
            raise PermissionDenied()

        return result

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        context_data['comment_form'] = NewCommentForm()
        context_data['rent_form'] = EditRentForm(instance=self.object)
        context_data['add_game_form'] = AddGameForm(date_from=self.object.date_from, date_to=self.object.date_to)

        return context_data


class NewCommentView(LoginRequiredMixin, FormView):
    """Creating a new comment."""
    form_class = NewCommentForm

    def get_object(self):
        return get_object_or_404(Rent, pk=self.kwargs['rent_pk'])

    def get(self, request, *args, **kwargs):
        return redirect(self.get_object().get_absolute_url())

    def form_valid(self, form):
        rent = self.get_object()
        user = self.request.user
        message = form.cleaned_data['comment']

        if rent.renter == user or user.has_perm('rent.manage_rents'):
            comment = Comment.objects.create(rent=rent, user=user, message=message)
            if rent.notify_new_comment(comment):
                messages.success(self.request, _("Successfully sent!"))
            else:
                messages.warning(self.request, _("Comment successfully sent, but failed to send notification emails!"))
        else:
            raise SuspiciousOperation("No permissions for comment this rent!")

        return redirect(rent.get_absolute_url())

    def form_invalid(self, form):
        messages.error(self.request, _("Invalid form!"))
        return redirect(self.get_object().get_absolute_url())


class EditView(PermissionRequiredMixin, UpdateView):
    """Admin view for editing a rent object."""
    model = Rent
    form_class = EditRentForm
    permission_required = 'rent.manage_rents'
    raise_exception = True

    def get(self, request, *args, **kwargs):
        return redirect(self.get_object().get_absolute_url())

    def form_valid(self, form):
        messages.success(self.request, _("Rent changed!"))
        r = super().form_valid(form)
        cleaned_data = form.cleaned_data
        changed_data = form.changed_data
        user = self.request.user
        object = self.get_object()

        if 'date_to' in changed_data or 'date_from' in changed_data:
            if not object.notify_changed_date(user):
                messages.error(self.request, _("Failed to send notification emails!"))

        new_renter = cleaned_data.get('renter') if 'renter' in changed_data else None
        new_date_to = cleaned_data.get('date_to') if 'date_to' in changed_data else None
        new_date_from = cleaned_data.get('date_from') if 'date_from' in changed_data else None
        if new_renter or new_date_from or new_date_to:
            object.create_new_history(user,
                                      new_renter=new_renter,
                                      edited_date_from=new_date_from,
                                      edited_date_to=new_date_to)

        return r

    def form_invalid(self, form):
        if form.error_text:
            messages.error(self.request, form.error_text)
        else:
            messages.error(self.request, _("Invalid form."))

        return redirect(self.get_object().get_absolute_url())

    def get_success_url(self):
        return self.get_object().get_absolute_url()


class ChangeStatusView(LoginRequiredMixin, View):
    """View for changing the status of the given rent."""

    http_method_names = ['get', ]

    def handle_rent(self, rent, status, user):
        # if has no permission, then can change only his own rent and only to cancelled
        if not user.has_perm('rent.manage_rents') and (
                user != rent.renter or
                status != Rent.STATUS_CANCELLED[0]):

            raise PermissionDenied("No permission to change status of rent!")

        if status == rent.status:
            messages.error(self.request, _("Cannot change rent status to the same!"))
            return redirect(rent.get_absolute_url())

        # check game availability if rent was cancelled or declined
        if rent.status in (Rent.STATUS_CANCELLED[0], Rent.STATUS_DECLINED[0]):
            not_free = []
            for game in rent.games.all():
                if not game.is_free(rent.date_from, rent.date_to):
                    not_free.append(str(game))
            if not_free:
                messages.error(
                    self.request,
                    _("Failed to change status! Following games are not available anymore: %s") % ','.join(not_free)
                )
                return redirect(rent.get_absolute_url())

        # save new status
        old_status = rent.status
        if status == Rent.STATUS_GAVE_OUT[0]:
            rent.date_from = datetime.now()
            if rent.date_to < rent.date_from:
                rent.date_to = rent.date_from
                messages.warning(self.request, _("End date is in the past! Please set a correct end date!"))

        rent.status = status
        rent.save()
        rent.create_new_history(self.request.user, new_status=status)

        # notify user in case last status is not inmyroom
        if old_status != Rent.STATUS_IN_MY_ROOM[0]:
            if not rent.notify_new_status(self.request.user):
                messages.error(self.request, _("Failed to send notification email!"))
        else:
            messages.success(self.request, _("User was not notified about this status change."))

    def get(self, request, *args, **kwargs):
        status = kwargs.get('status')
        user = self.request.user

        # batch processing status change
        successful = 0
        pks = kwargs.get('rent_pk').split(',')

        for pk in pks:
            try:
                rent = Rent.objects.get(pk=pk)
                self.handle_rent(rent, status, user)
                successful += 1

                # if there's only one change, redirect
                if len(pks) == 1:
                    return redirect(rent.get_absolute_url())
            except Rent.DoesNotExist:
                pass

        if len(pks) != successful:
            messages.error(self.request, "Only %d change was successful out of %d" % (successful, len(pks)))

        return redirect(reverse_lazy('rent:rents'))


class AddGameView(PermissionRequiredMixin, FormView):
    """Adding a game to an already existing rent object."""

    permission_required = 'rent.manage_rents'
    raise_exception = True
    form_class = AddGameForm

    def get_rent(self):
        return get_object_or_404(Rent, pk=self.kwargs.get('rent_pk'))

    def form_valid(self, form):
        rent = self.get_rent()
        game = get_object_or_404(GamePiece, pk=form.cleaned_data['game'])
        if game.is_free(rent.date_from, rent.date_to):
            rent.games.add(game)
            rent.create_new_history(self.request.user, added_game=game)
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
    """Removing a game from an already existing rent object."""

    http_method_names = ['get', ]
    permission_required = 'rent.manage_rents'
    raise_exception = True

    def get(self, request, *args, **kwargs):
        rent = get_object_or_404(Rent, pk=kwargs.get('rent_pk'))
        game_piece = get_object_or_404(GamePiece, pk=kwargs.get('game_pk'))

        if game_piece in rent.games.all():
            rent.games.remove(game_piece)
            rent.create_new_history(self.request.user, deleted_game=game_piece)
            rent.save()
        else:
            messages.error(self.request, _("Given game is not in the rent!"))
            logger.error("Given game is not in the rent!")

        return redirect(rent.get_absolute_url())


class RentRules(TemplateView):
    """Displaying static page about our rules."""
    template_name = "static_pages/rent_rules.html"
