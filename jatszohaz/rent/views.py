import logging
from django.conf import settings

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import SuspiciousOperation, PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, DetailView, UpdateView, FormView, View, TemplateView
from formtools.wizard.views import SessionWizardView

from .forms import RentFormStep1, RentFormStep2, RentFormStep3, NewCommentForm, EditRentForm, AddGameForm
from inventory.models import GameGroup
from .models import Rent, Comment, GamePiece


logger = logging.getLogger(__name__)


class NewView(LoginRequiredMixin, SessionWizardView):
    template_name = "rent/new_rent.html"
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
            data['game_groups'] = step1_data.get('1-game_groups', ())

        return self.initial_dict.get(step, data)

    def send_email(self, rent, comment):
        """Sends notification email to mailing list"""

        recipient = settings.NOTIFICATION_EMAIL_TO
        if recipient:
            data = {
                'url': rent.get_absolute_url(),
                'renter': rent.renter.full_name2(),
                'date_from': rent.date_from,
                'date_to': rent.date_to,
                'games': ', '.join([gp.game_group.name for gp in rent.games.all()]),
                'comment': comment.message
            }
            subject = _("%s new rent") % settings.EMAIL_SUBJECT_PREFIX
            message = _("Hi!<br/>New rent created!<br/><br/>"
                        "Renter: %(renter)s<br/>"
                        "Dates: %(date_from)s - %(date_to)s<br/>"
                        "Games: %(games)s<br/>"
                        "Comment: %(comment)s<br/>"
                        "Details: <a href=\"%(url)s\">%(url)s<a><br/><br/>"
                        "Best wishes,<br/>Játszóház") % data

            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient, ], fail_silently=False)
            except Exception as e:
                logger.error("Failed to send email! %s" % e)
                return False

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
        for gg_id in game_groups or ():
            gg = GameGroup.objects.get(id=gg_id)
            rent.games.add(gg.get_game_piece(date_from, date_to))
        rent.save()
        comment = Comment.objects.create(
            rent=rent,
            user=user,
            message=comment
        )

        self.send_email(rent, comment)

        messages.success(self.request, _("Successfully rented!"))
        return redirect(rent.get_absolute_url())


class MyView(LoginRequiredMixin, ListView):
    model = Rent
    template_name = "rent/my_rents.html"
    ordering = ['-created']
    paginate_by = 5

    def get_queryset(self):
        return self.request.user.rents.all()


class RentsView(PermissionRequiredMixin, ListView):
    model = Rent
    template_name = "rent/rents.html"
    permission_required = 'rent.manage_rents'
    paginate_by = 5

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

        return context


class DetailsView(LoginRequiredMixin, DetailView):
    model = Rent
    template_name = "rent/rent_detail.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        context_data['comment_form'] = NewCommentForm()
        context_data['rent_form'] = EditRentForm(instance=self.object)
        context_data['add_game_form'] = AddGameForm(date_from=self.object.date_from, date_to=self.object.date_to)

        # set available statuses based on current status
        available_statuses = []
        if self.object.status in (Rent.STATUS_DECLINED[0], Rent.STATUS_CANCELLED[0], Rent.STATUS_PENDING[0]):
            available_statuses.append(Rent.STATUS_APPROVED)
        if self.object.status == Rent.STATUS_APPROVED[0]:
            available_statuses.append(Rent.STATUS_GAVE_OUT)
        if self.object.status == Rent.STATUS_GAVE_OUT[0]:
            available_statuses.append(Rent.STATUS_IN_MY_ROOM)
        if self.object.status in (Rent.STATUS_IN_MY_ROOM[0], Rent.STATUS_GAVE_OUT[0]):
            available_statuses.append(Rent.STATUS_BACK)
        if self.object.status in (Rent.STATUS_PENDING[0], Rent.STATUS_APPROVED[0]):
            available_statuses.append(Rent.STATUS_DECLINED)
        if self.object.status in (Rent.STATUS_PENDING[0], Rent.STATUS_APPROVED[0]):
            available_statuses.append(Rent.STATUS_CANCELLED)
        context_data['available_statuses'] = available_statuses

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

        if rent.renter == user or user.has_perm('rent.manage_rents'):
            comment = Comment.objects.create(rent=rent, user=user, message=message)
            if rent.notify_new_comment(comment):
                messages.success(self.request, _("Successfully sent!"))
            else:
                messages.warning(self.request, _("Comment successfully sent, but failed to send notification emails!"))
        else:
            raise SuspiciousOperation("No permissions for comment this rent!")

        return redirect(rent.get_absolute_url())


class EditView(PermissionRequiredMixin, UpdateView):
    model = Rent
    form_class = EditRentForm
    permission_required = 'rent.manage_rents'
    raise_exception = True

    def get(self, request, *args, **kwargs):
        return redirect(self.get_object().get_absolute_url())

    def form_valid(self, form):
        messages.success(self.request, _("Rent changed!"))
        r = super().form_valid(form)

        if 'date_to' in form.changed_data or 'date_from' in form.changed_data:
            if not self.get_object().notify_changed_date(self.request.user):
                messages.error(self.request, _("Failed to send notification emails!"))

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
    http_method_names = ['get', ]

    def get(self, request, *args, **kwargs):
        rent = get_object_or_404(Rent, pk=kwargs.get('rent_pk'))
        status = kwargs.get('status')
        user = self.request.user

        # if has no permission, then can change only his own rent and only to cancelled
        if not user.has_perm('rent.manage_rents') and (
                user != rent.renter or
                status != Rent.STATUS_CANCELLED[0]):

            raise PermissionDenied("No permission to change status of rent!")

        rent.status = status
        rent.save()
        rent.create_new_history(self.request.user)

        if not rent.notify_new_status(self.request.user):
            messages.error(self.request, _("Failed to send notification email!"))

        return redirect(rent.get_absolute_url())


class AddGameView(PermissionRequiredMixin, FormView):
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
    permission_required = 'rent.manage_rents'
    raise_exception = True

    def get(self, request, *args, **kwargs):
        rent = get_object_or_404(Rent, pk=kwargs.get('rent_pk'))
        game_piece = get_object_or_404(GamePiece, pk=kwargs.get('game_pk'))
        rent.games.remove(game_piece)
        rent.save()
        return redirect(rent.get_absolute_url())


class RentRules(TemplateView):
    template_name = "static_pages/rent_rules.html"
