from django.db.models import F, Max, Q, Sum

__all__ = (
    'get_or_none', 'get_pk_or_none', 'get_sum',
    'get_max', 'do_filter',
)


def get_or_none(model_class, *args, **kwargs):
    try:
        return model_class.objects.get(*args, **kwargs)
    except Exception:
        return None


def get_pk_or_none(model_class, *args, **kwargs):
    obj = get_or_none(model_class, *args, **kwargs)
    return obj.pk if obj else None


def get_sum(qs, field):
    """
    get sum for queryset.

    ``qs``: queryset
    ``field``: The field name to sum.
    """
    sum_field = '%s__sum' % field
    qty = qs.aggregate(Sum(field))[sum_field]
    return qty if qty else 0


def get_max(qs, field):
    """
    get max for queryset.

    qs: queryset
    field: The field name to max.
    """
    max_field = '%s__max' % field
    num = qs.aggregate(Max(field))[max_field]
    return num if num else 0


def do_filter(qs, qdata, quick_query_fields=[], int_quick_query_fields=[]):
    """
    auto filter queryset by dict.

    qs: queryset need to filter.
    qdata:
    quick_query_fields:
    int_quick_query_fields:
    """
    try:
        qs = qs.filter(
            __gen_quick_query_params(
                qdata.get('q_quick_search_kw'), quick_query_fields,
                int_quick_query_fields)
        )
        q, kw_query_params = __gen_query_params(qdata)
        qs = qs.filter(q, **kw_query_params)
    except:
        import traceback
        traceback.print_exc()
    return qs


def __gen_quick_query_params(value, fields, int_fields):
    q = Q()
    if not value:
        return q
    for field in fields:
        d = {"%s__icontains" % field: value}
        q = q | Q(**d)
    if value.isdigit():
        for f in int_fields:
            d = {f: value}
            q = q | Q(**d)
    return q


def __gen_query_params(qdata):
    q = Q()
    kw_query_params = {}
    for k, v in qdata.items():
        if k.startswith('q__'):
            k = k[3:]
            if not isinstance(v, str):
                if v is not None:
                    kw_query_params[k] = v
                continue
            if v == '':
                continue
            v = v.replace('，', ',')
            if v.startswith('F__'):
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
            if isinstance(v, str):
                v = {'__True': True, '__False': False}.get(v, v)
            kw_query_params[k] = v
    return q, kw_query_params
