from django.utils.dateparse import parse_date


def parse_get_date(request, param_name):
    """
    Parses GET parameter as date.
    Raises ValueError if the date is invalid.
    :return: (get_data, date) tuple, containing the original data and
     either a valid datetime object or None if not given.
    """

    get_date = request.GET.get(param_name, None)
    if get_date:
        date = parse_date(get_date)
        if not date:
            raise ValueError()
        return get_date, date
    return get_date, None
