# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.http import HttpResponse


def request_get_next(request, default_next):
    next = request.POST.get('next')
    if not next:
        next = request.GET.get('next')
    if not next:
        next = request.META.get('HTTP_REFERER', None)
    if not next:
        next = default_next
    return next


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def save_formset(formset, ext_vals):
    formset.save(commit=False)
    for f in formset.saved_forms:
        o = f.save(commit=False)
        for k, v in ext_vals.items():
            setattr(o, k, v)
        o.save()


def render_json(data, ensure_ascii=False):
    return HttpResponse(json.dumps(data), mimetype="application/json")
