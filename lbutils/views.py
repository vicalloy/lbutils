import json

from django.http import HttpResponse

try:
    from crispy_forms.helper import FormHelper
except ImportError:
    pass


__all__ = (
    'qdict_get_list', 'request_get_next', 'save_formset',
    'render_json', 'has_any_perm', 'get_post_data',
    'get_client_ip', 'create_formset', 'forms_is_valid',
)


def qdict_get_list(qdict, k):
    """
    get list from QueryDict and remove blank date from list.
    """
    pks = qdict.getlist(k)
    return [e for e in pks if e]


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


def render_json(data, ensure_ascii=False, request=None, as_text=False):
    fmt = 'json'
    content_type = "application/json"
    if as_text:
        content_type = "text/html"
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


def create_formset(
        formset_class, prefix,
        template_prefix=None, **kwargs):
    helper = FormHelper()
    template = 'bootstrap3/table_inline_formset.html'
    if template_prefix:
        template = "%s/%s" % (template_prefix, template)
    helper.template = template
    formset = formset_class(prefix=prefix, **kwargs)
    formset.helper = helper
    return formset


def forms_is_valid(forms):
    return all([form.is_valid() for form in forms])
