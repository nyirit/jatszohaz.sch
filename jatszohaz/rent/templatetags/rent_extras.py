from django import template

register = template.Library()


@register.inclusion_tag('rent/rent_statuses.html')
def show_rent_available_statuses(rent, user, *args):
    return {'statuses': rent.get_available_statuses(user),
            'rent_pk': rent.pk}
