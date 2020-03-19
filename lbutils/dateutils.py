from datetime import datetime

__all__ = (
    'get_month_choices', 'MONTH_CHOICES', 'fmt_month',
    'get_year_choices', 'fmt_datetime',
)


def get_month_choices(blank_label='------'):
    choices = [
        ('01', '01'),
        ('02', '02'),
        ('03', '03'),
        ('04', '04'),
        ('05', '05'),
        ('06', '06'),
        ('07', '07'),
        ('08', '08'),
        ('09', '09'),
        ('10', '10'),
        ('11', '11'),
        ('12', '12'),
    ]
    if blank_label:
        choices.insert(0, ('', blank_label))
    return choices


MONTH_CHOICES = get_month_choices(None)


def fmt_month(month):
    """ format month(1 to 01) """
    if not month:
        return month
    return ("%s" % month).zfill(2)


def get_year_choices(start_year=-5, end_year=2, blank_label=''):
    year = datetime.today().year
    years = range(year + start_year, year + end_year)
    choices = [(e, e) for e in years]
    if blank_label:
        choices.insert(0, ('', blank_label))
    return choices


def fmt_datetime(d, fmt='', local=True):
    """
    format date with local support
    ``d``: datetime to format
    ``fmt``: format, default is '%Y-%m-%d %H-%M'
    ``local``: format as local time
    """
    if not d:
        return ''
    if local:
        from django.templatetags.tz import localtime
        d = localtime(d)
    if not fmt:
        fmt = '%Y-%m-%d %H-%M'
    return d.strftime(fmt)
