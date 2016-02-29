from __future__ import unicode_literals


import importlib
from django.template.defaultfilters import floatformat
from django.contrib.humanize.templatetags.humanize import intcomma


def safe_eval(source, *args, **kwargs):
    """ eval without import """
    source = source.replace('import', '')  # import is not allowed
    return eval(source, *args, **kwargs)


def fmt_num(num, zero_num=None):
    """ humanize number(9000 to 9,000) """
    if zero_num is not None:
        num = floatformat(num, zero_num)
    return intcomma(num, False)


def create_class(class_name, *args, **kwargs):
    """ create class instance
    class_name: name of class ex: "django.http.HttpResponse"
    *args, **kwargs: param for class
    """
    idx = class_name.rindex(r'.')
    _module = importlib.import_module(class_name[:idx])
    class_name = class_name[idx + 1:]
    return getattr(_module, class_name)(*args, **kwargs)
