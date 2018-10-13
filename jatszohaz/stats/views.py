from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.views.generic import TemplateView
from rent.models import Rent


class StatsView(PermissionRequiredMixin, TemplateView):
    permission_required = 'rent.view_stat'
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
