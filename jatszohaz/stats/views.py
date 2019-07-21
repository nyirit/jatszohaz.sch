from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count, F, Q
from django.db.models.functions import TruncMonth
from django.http import Http404
from django.views.generic import TemplateView
from inventory.models import GameGroup
from jatszohaz.models import JhUser
from rent.models import Rent, RentHistory
from stats.utils import parse_get_date


class StatBase(PermissionRequiredMixin, TemplateView):
    permission_required = 'rent.view_stat'


class StatsView(StatBase):
    """Overview page showing the count of rents by month."""

    template_name = 'stats/overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        context['monthly_rents'] = Rent.objects\
            .annotate(month=TruncMonth('date_from'))\
            .values('month')\
            .annotate(count=Count('id'))\
            .order_by('-month')\
            .all()

        return context


class MembersView(StatBase):
    """Showing number of handled rents by users."""

    template_name = 'stats/members.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        try:
            get_date_from, date_from = parse_get_date(self.request, 'from')
            get_date_to, date_to = parse_get_date(self.request, 'to')
        except ValueError:
            # handle datetime format exceptions
            raise Http404()

        queryset = RentHistory.objects.exclude(user=F('rent__renter'))

        if date_from:
            queryset = queryset.filter(rent__created__gte=date_from)
        if date_to:
            queryset = queryset.filter(rent__created__lte=date_to)

        # todo solve this with a much faster subquery
        rents_users = []
        for user in JhUser.objects.order_by('last_name', 'first_name').all():
            rents_count = queryset.filter(user=user).values('rent').distinct().count()
            if rents_count > 0:
                rents_users.append({
                    'user': user.full_name2(),
                    'count': rents_count,
                })

        context['rents_users'] = sorted(rents_users, key=lambda e: e['count'], reverse=True)
        context['date_from'] = get_date_from
        context['date_to'] = get_date_to

        return context


class GamesView(StatBase):
    """Showing how many times certain games were rented."""

    template_name = 'stats/games.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        # parse filters
        try:
            get_date_from, date_from = parse_get_date(self.request, 'from')
            get_date_to, date_to = parse_get_date(self.request, 'to')
        except ValueError:
            # handle datetime format exceptions
            raise Http404()

        # do not include DECLINED and CANCELLED rents
        included_statuses = (Rent.STATUS_PENDING[0], Rent.STATUS_APPROVED[0], Rent.STATUS_GAVE_OUT[0],
                             Rent.STATUS_IN_MY_ROOM[0], Rent.STATUS_BACK[0])
        count_filter = {
            'game_pieces__rents__status__in': included_statuses,
        }

        # apply filters for count
        if date_from:
            count_filter['game_pieces__rents__date_from__gte'] = date_from
        if date_to:
            count_filter['game_pieces__rents__date_from__lte'] = date_to

        queryset = GameGroup.objects\
            .annotate(rcount=Count('game_pieces__rents', filter=Q(**count_filter)))\
            .values('rcount', 'name').order_by('-rcount', 'name')

        context['stat_data'] = queryset.all()
        context['date_from'] = get_date_from
        context['date_to'] = get_date_to
        return context
