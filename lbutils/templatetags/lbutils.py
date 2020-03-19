from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def get_setting(context, key, default_val="", as_key=None):
    """
    get val form settings and set to context
      {% load lbutils %}
      {% get_setting "key" default_val "as_key" %}
      {{ as_key }}
      if as_key is None, this tag will return val
    """
    if ("%s" % default_val).startswith('$.'):
        default_val = getattr(settings, default_val[2:])
    val = getattr(settings, key, default_val)
    if not as_key:
        return val
    context[as_key] = val
    return ''


@register.filter(name='boolean_icon')
def boolean_icon(v):
    if v:
        return mark_safe('<i class="fa fa-fw fa-check-circle"/>')
    return ''


@register.filter(name='display_array')
def display_array(objs):
    if not objs:
        return ''
    return ', '.join(['%s' % e for e in objs])


@register.simple_tag
def getvars(request, excludes):
    getvars = request.GET.copy()
    excludes = excludes.split(',')
    for p in excludes:
        if p in getvars:
            del getvars[p]
        if len(getvars.keys()) > 0:
            return "&%s" % getvars.urlencode()
        else:
            return ''
