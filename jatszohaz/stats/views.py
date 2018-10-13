from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count, F
from django.db.models.functions import TruncMonth
from django.http import Http404
from django.utils.dateparse import parse_date
from django.views.generic import TemplateView
from rent.models import Rent, RentHistory


class StatBase(PermissionRequiredMixin, TemplateView):
    permission_required = 'rent.view_stat'


class StatsView(StatBase):
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
    permission_required = 'rent.view_stat'
    template_name = 'stats/members.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        get_date_from = self.request.GET.get('from', None)
        get_date_to = self.request.GET.get('to', None)
        queryset = RentHistory.objects\
            .exclude(user=F('rent__renter'))

        try:
            if get_date_from:
                date_from = parse_date(get_date_from)
                if not date_from:
                    raise Http404()
                queryset = queryset.filter(rent__created__gte=date_from)
            if get_date_to:
                date_to = parse_date(get_date_to)
                if not date_to:
                    raise Http404()
                queryset = queryset.filter(rent__created__lte=date_to)
        except ValueError:
            # handle datetime format exceptions
            raise Http404()

        context['rents_users'] = queryset\
            .values('user__first_name', 'user__last_name')\
            .annotate(count=Count('id'))\
            .order_by('-count')\
            .all()
        context['date_from'] = get_date_from
        context['date_to'] = get_date_to

        return context
