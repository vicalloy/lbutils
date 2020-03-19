import importlib
import math

from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaultfilters import floatformat

__all__ = (
    'safe_eval', 'fmt_num', 'as_callable', 'create_instance',
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


def as_callable(callable_path):
    if callable(callable_path):
        return callable_path
    idx = callable_path.rindex(r'.')
    _module = importlib.import_module(callable_path[:idx])
    return getattr(_module, callable_path[idx + 1:])


def create_instance(class_name, *args, **kwargs):
    """
    create class instance

    class_name: name of class i.e.: "django.http.HttpResponse"
    *args, **kwargs: param for class
    """
    return as_callable(class_name)(*args, **kwargs)


def format_filesize(size):
    if (size < 1024):
        return '%s B' % size
    size = size / 1024.0
    size_name = ("KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size, 1024)))
    p = math.pow(1024, i)
    s = round(size / p, 2)
    return '%s %s' % (s, size_name[i])
