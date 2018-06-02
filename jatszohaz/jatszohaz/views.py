import logging
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.messages.views import SuccessMessageMixin
from django.core import signing
from django.core.exceptions import SuspiciousOperation, PermissionDenied
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, RedirectView, View

from braces.views import PermissionRequiredMixin

from .forms import JhUserForm
from inventory.models import GameGroup
from .models import JhUser

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = "jatszohaz/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data()
        if not self.request.user.is_anonymous:
            ctx['username'] = self.request.user.full_name2()
        return ctx


class CalendarView(TemplateView):
    template_name = "jatszohaz/calendar.html"


class GamesView(ListView):
    model = GameGroup
    template_name = "jatszohaz/games.html"
    ordering = "name"
    queryset = GameGroup.objects.filter(hide=False)


class MyProfileView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = JhUser
    success_url = reverse_lazy('my-profile')
    success_message = _("Successfully updated!")
    form_class = JhUserForm
    template_name = "jatszohaz/profile.html"

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        user = self.request.user
        user.checked_profile = True
        user.save()

        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, DetailView):
    model = JhUser
    template_name = "jatszohaz/profile_detail.html"
    permission_required = 'jatszohaz.view_all'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rents'] = self.object.rents.all()
        context['user_groups'] = ','.join([g.name for g in self.object.groups.all()])
        context['allowed_groups'] = ProfileAddRemoveGroups.allowed_groups
        if self.request.user.has_perm('jatszohaz.leader_admin') and not self.request.user == self.get_object():
            context['token_login'] = TokenLogin.get_token_url(self.object, self.request.user)
        return context


class ProfileAddRemoveGroups(PermissionRequiredMixin, View):
    http_method_names = ['get', ]
    permission_required = 'jatszohaz.leader_admin'
    raise_exception = True
    allowed_groups = ('kortag', 'leader', )

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(JhUser, pk=kwargs.get('user_pk'))
        group = get_object_or_404(Group, name=kwargs.get('group_name'))

        if group.name not in self.allowed_groups:
            raise PermissionDenied("Group not in allowed groups.")

        if user in group.user_set.all():
            group.user_set.remove(user)
            messages.success(request, _("%s removed from group %s") % (user.full_name2(), group.name))
        else:
            group.user_set.add(user)
            messages.success(request, _("%s added to group %s") % (user.full_name2(), group.name))

        return redirect(user.get_absolute_url())


class AboutUsView(TemplateView):
    template_name = "static_pages/about_us.html"


class FaqView(TemplateView):
    template_name = "static_pages/faq.html"


class AfterLoginView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        if not self.request.user.checked_profile:
            messages.info(self.request, _("Please check your profile data and click the Update button!"))
            return reverse_lazy('my-profile')

        return reverse_lazy('home')


class UsersView(PermissionRequiredMixin, ListView):
    model = JhUser
    permission_required = 'jatszohaz.view_all'
    template_name = "jatszohaz/user_list.html"
    paginate_by = 50


class AdminRules(PermissionRequiredMixin, TemplateView):
    template_name = "static_pages/admin_rules.html"
    permission_required = 'jatszohaz.basic_admin'


class TokenLogin(View):
    token_max_age = 120  # seconds

    @classmethod
    def get_token(cls, user, sudoer):
        return signing.dumps((sudoer.pk, user.pk),
                             salt=settings.SECRET_KEY, compress=True)

    @classmethod
    def get_token_url(cls, user, sudoer):
        key = cls.get_token(user, sudoer)
        return reverse_lazy("token-login", args=(key, ))

    def get(self, request, token, *args, **kwargs):
        try:
            data = signing.loads(token, salt=settings.SECRET_KEY,
                                 max_age=self.token_max_age)
            logger.debug('TokenLogin token data: %s', str(data))
            sudoer, user = data
            logger.debug('Extracted TokenLogin data: sudoer: %s, user: %s',
                         str(sudoer), str(user))
        except (signing.BadSignature, ValueError, TypeError) as e:
            logger.warning('Tried invalid TokenLogin token. '
                           'Token: %s, user: %s. %s',
                           token, str(self.request.user), str(e))
            raise SuspiciousOperation
        sudoer = get_user_model().objects.get(pk=sudoer)
        if not sudoer.has_perm('jatszohaz.leader_admin'):
            raise PermissionDenied
        user = get_user_model().objects.get(pk=user)
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        logger.warning('%s %d logged in as user %s %d',
                       str(sudoer), sudoer.pk, str(user), user.pk)
        login(request, user)
        messages.info(request, _("Logged in as user %s.") % str(user))
        return redirect("/")
