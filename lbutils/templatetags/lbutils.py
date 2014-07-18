# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def get_setting(context, key, default_val="", as_key=None):
    """
    get val form settings and set to context
      {% load swift %}
      {% get_setting "key" default_val "as_key" %}
      {{ as_key }}
      if as_key is None, this tag will return val
    """
    #as_key = as_key if as_key else key
    if ("%s" % default_val).startswith('$.'):
        default_val = getattr(settings, default_val[2:])
    val = getattr(settings, key, default_val)
    if not as_key:
        return val
    context[as_key] = val
    return ''
