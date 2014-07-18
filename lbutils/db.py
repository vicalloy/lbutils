# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from django.db.models import Q, F
from django.db.models import Sum


def get_sum(qs, field):
    sum_field = '%s__sum' % field
    qty = qs.aggregate(Sum(field))[sum_field]
    return qty if qty else 0


def do_filter(qs, qdata, quick_query_fields=[]):
    try:
        qs = qs.filter(
            gen_quick_query_params(qdata.get('q_quick_search_kw'), quick_query_fields)
        )
        q, kw_query_params = gen_query_params(qdata)
        qs = qs.filter(q, **kw_query_params)
    except:
        import traceback
        traceback.print_exc()
    return qs


def gen_quick_query_params(value, fields):
    q = Q()
    if not value:
        return q
    for field in fields:
        d = {"%s__icontains" % field: value}
        q = q | Q(**d)
    return q


def gen_query_params(qdata):
    q = Q()
    kw_query_params = {}
    for k, v in qdata.items():
        if k.startswith('q__'):
            if not isinstance(v, (str, unicode)):
                if v is not None:
                    kw_query_params[k] = v
                continue
            if v == '':
                continue
            v = v.replace('，', ',')
            k = k[3:]
            if k.startswith('d__'):
                k = k[3:]
                if v:
                    v = datetime.datetime.strptime(v, "%Y-%m-%d").date()
                    kw_query_params[k] = v
                continue
            elif v.startswith('F__'):
                v = F(v[3:])
            elif k.endswith('__in'):
                v = [e for e in v.split(',') if e]
            elif ',' in v:
                tmp_q = Q()
                v = [e for e in v.split(',') if e]
                for o in v:
                    tmp_q = tmp_q | Q(**{k: o})
                q = q & tmp_q
                continue
            if isinstance(v, (str, unicode)):
                v = {'__True': True, '__False': False}.get(v, v)
            kw_query_params[k] = v
    return q, kw_query_params
