from __future__ import unicode_literals


import importlib
from django.template.defaultfilters import floatformat
from django.contrib.humanize.templatetags.humanize import intcomma


__all__ = (
    'safe_eval', 'fmt_num', 'create_instance',
    'format_filesize',
)


def safe_eval(source, *args, **kwargs):
    """ eval without import """
    source = source.replace('import', '')  # import is not allowed
    return eval(source, *args, **kwargs)


def fmt_num(num, zero_num=None):
    """ humanize number(9000 to 9,000) """
    if zero_num is not None:
        num = floatformat(num, zero_num)
    return intcomma(num, False)


def create_instance(class_name, *args, **kwargs):
    """
    create class instance

    class_name: name of class i.e.: "django.http.HttpResponse"
    *args, **kwargs: param for class
    """
    idx = class_name.rindex(r'.')
    _module = importlib.import_module(class_name[:idx])
    class_name = class_name[idx + 1:]
    return getattr(_module, class_name)(*args, **kwargs)


def format_filesize(size_in_bytes):
    SIZE_KEYS = ['B', 'KB', 'MB']
    try:
        size_in_bytes = int(size_in_bytes)
    except ValueError:
        return size_in_bytes
    if size_in_bytes < 1:
        return '%d %s' % (0, SIZE_KEYS[2])
    size_in_bytes, divider = int(size_in_bytes), 1 << 20
    major = size_in_bytes / divider
    while not major:
        major = size_in_bytes / divider
        if not major:
            divider >>= 10
    rest = size_in_bytes - major * divider
    scale = 10
    fract = int(float(rest) / divider * scale)
    cnt = 0
    while divider:
        cnt += 1
        divider >>= 10
    value = major + fract * (1.0 / scale)
    ivalue = int(value)
    if value == ivalue:
        value = ivalue
    return '%d %s' % (value, SIZE_KEYS[cnt - 1])
