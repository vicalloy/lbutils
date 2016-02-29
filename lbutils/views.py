# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.http import HttpResponse

try:
    from crispy_forms.helper import FormHelper
except ImportError:
    pass


def get_pks(qdict, k):
    """ get list from QueryDict, if not find return []  """
    try:
        pks = qdict.getlist(k)
        return [e for e in pks if e]
    except Exception:
        pass
    return []


def request_get_next(request, default_next):
    """
    get next url form request
    order: POST.next GET.next HTTP_REFERER, default_next
    """
    next_url = request.POST.get('next')\
        or request.GET.get('next')\
        or request.META.get('HTTP_REFERER')\
        or default_next
    return next_url


def save_formset(formset, ext_vals):
    formset.save(commit=False)
    for f in formset.saved_forms:
        o = f.save(commit=False)
        for k, v in ext_vals.items():
            setattr(o, k, v)
        o.save()


def render_json(data, ensure_ascii=False, request=None):
    fmt = 'json'
    content_type = "text/html"  # application/json
    plain = json.dumps(data, ensure_ascii=False)
    if request:
        fmt = request.GET.get('fmt', 'json')
        if fmt == "jsonp":
            jsonp_cb = request.GET.get('callback', 'callback')
            # content_type = "application/javascript"
            plain = "%s(%s);" % (jsonp_cb, plain)
    return HttpResponse(plain, content_type=content_type)


def has_any_perm(user, perms):
    if not isinstance(perms, [list, tuple]):
        perms = [e.strip() for e in perms.split(',') if e.strip()]
    for p in perms:
        if user.has_perm(p):
            return True
    return False


def get_post_data(request):
    """ get request.POST, if POST is empty return None """
    if request.method == 'POST':
        return request.POST
    return None


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def create_formset(formset_class, prefix, **kwargs):
    helper = FormHelper()
    helper.template = 'swift/bootstrap3/table_inline_formset.html'
    formset = formset_class(prefix=prefix, **kwargs)
    formset.helper = helper
    return formset


def forms_is_valid(forms):
    is_valid = True
    for form in forms:
        is_valid = is_valid and form.is_valid()
    return is_valid
