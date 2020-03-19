from django import forms
from django.forms.formsets import BaseFormSet
from django.forms.models import BaseInlineFormSet, BaseModelFormSet
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from .widgets import JustSelectedSelectMultiple, TextWidget

try:
    from crispy_forms.bootstrap import PrependedText
    from crispy_forms.helper import FormHelper
    from crispy_forms.layout import Layout
    from crispy_forms.bootstrap import StrictButton
    from crispy_forms.layout import Div
except ImportError:
    pass


__all__ = (
    'FormHelperMixin', 'BootstrapFormHelperMixin', 'QuickSearchForm', 'LBBaseFormSet',
    'LBBaseModelFormSet', 'LBBaseInlineFormSet', 'row_div',
)


class FormHelperMixin(object):

    def errors_as_text(self):
        """
        only available to Django 1.7+
        """
        errors = []
        errors.append(self.non_field_errors().as_text())
        errors_data = self.errors.as_data()
        for key, value in errors_data.items():
            field_label = self.fields[key].label
            err_descn = ''.join([force_text(e.message) for e in value])
            error = "%s %s" % (field_label, err_descn)
            errors.append(error)
        return ','.join(errors)

    def as_readonly_fields(self, fields=[], exclude=[], include_all_if_empty=True):
        self.add_attr2fields(
            'readonly', 'readonly',
            fields=fields, exclude=exclude, include_all_if_empty=True)

    def as_text_fields(self, fields=[], exclude=[], include_all_if_empty=True):
        for f in self.filter_fields(fields, exclude, include_all_if_empty):
            f = self.fields[f.name]
            f.widget = TextWidget(src_widget=f.widget)

    def as_hidden_fields(self, fields=[], exclude=[], include_all_if_empty=True):
        for f in self.filter_fields(fields, exclude, include_all_if_empty):
            f = self.fields[f.name]
            f.required = False
            if isinstance(f.widget, (forms.SelectMultiple, JustSelectedSelectMultiple)):
                f.widget = forms.MultipleHiddenInput()
            else:
                f.widget = forms.HiddenInput()

    def add_attr2fields(self, attr_name, attr_val, fields=[], exclude=[], include_all_if_empty=True):
        """
        add attr to fields
        """
        for f in self.filter_fields(fields, exclude, include_all_if_empty):
            f = self.fields[f.name]
            org_val = f.widget.attrs.get(attr_name, '')
            f.widget.attrs[attr_name] = '%s %s' % (org_val, attr_val) if org_val else attr_val

    def add_class2fields(self, html_class, fields=[], exclude=[], include_all_if_empty=True):
        """
        add class to html widgets.
        """
        self.add_attr2fields('class', html_class, fields, exclude)

    def filter_fields(self, fields=[], exclude=[], include_all_if_empty=True):
        """
        filter fields

        fields:
        exclude:
        include_all_if_empty: if fields is empty return all fields

        return: fileds
        """
        if not include_all_if_empty and not fields:
            return []
        ret = []
        for f in self.visible_fields():
            if fields and f.name not in fields:
                continue
            if exclude and f.name in exclude:
                continue
            ret.append(f)
        return ret

    def as_required_fields(self, fields=[]):
        """ set required to True """
        fields = self.filter_fields(fields)
        for f in fields:
            f = self.fields[f.name]
            f.required = True

    def check_uniqe(self, obj_class, error_msg=_('Must be unique'), **kwargs):
        """ check if this object is unique """
        if obj_class.objects.filter(**kwargs).exclude(pk=self.instance.pk):
            raise forms.ValidationError(error_msg)

    def row_div(self, fnames, span=4):
        fields = self.filter_fields(fnames)
        fnames = [e.name for e in fields if not e.is_hidden]
        return row_div(fnames, span=span)


class BootstrapFormHelperMixin(FormHelperMixin):

    def init_crispy_helper(self, label_class='col-md-2', field_class='col-md-4'):
        # multicolumn form http://www.bootply.com/s2mmi1YyL4#
        self.helper = helper = FormHelper()
        helper.field_template = 'bootstrap3/multicolumnsfield.html'
        helper.label_class = label_class
        helper.field_class = field_class
        helper.form_tag = False
        return helper

    def layout_fields(self, grouped_fields):
        divs = []
        one_row_fields = []
        for fields in grouped_fields:
            if len(fields) == 1:
                one_row_fields.extend(fields)
            divs.append(Div(*fields, css_class='form-group'),)
        self.helper.layout = Layout(*divs)
        self.one_row_fields = one_row_fields


class QuickSearchForm(FormHelperMixin, forms.Form):
    q_quick_search_kw = forms.CharField(label=_("Keyword"), required=False)

    def __init__(self, *args, **kw):
        super(QuickSearchForm, self).__init__(*args, **kw)
        self.add_class2fields('input-sm')
        self.helper = helper = FormHelper()
        helper.form_class = 'form-inline'
        helper.form_method = 'get'
        helper.field_template = 'bootstrap3/layout/inline_field.html'
        helper.layout = Layout(
            'q_quick_search_kw',
            StrictButton(_('Search'), type="submit", css_class='btn-sm btn-default'),
        )


class LBBaseFormSet(BaseFormSet):
    """
    Subclass for BaseFormSet.
    Add ext_data support for __init__.
    """

    def __init__(self, *args, **kwargs):
        self.ext_params = {}
        if 'ext_data' in kwargs:
            self.ext_params['ext_data'] = kwargs.pop('ext_data')
        super(LBBaseFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        kwargs.update(self.ext_params)
        return super(LBBaseFormSet, self)._construct_form(i, **kwargs)


class LBBaseModelFormSet(BaseModelFormSet):
    """
    Subclass for BaseModelFormSet
    Add ext_data support for __init__.
    """

    def __init__(self, *args, **kwargs):
        self.ext_params = {}
        if 'ext_data' in kwargs:
            self.ext_params['ext_data'] = kwargs.pop('ext_data')
        super(LBBaseModelFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        kwargs.update(self.ext_params)
        return super(LBBaseModelFormSet, self)._construct_form(i, **kwargs)


class LBBaseInlineFormSet(BaseInlineFormSet):
    """
    Subclass for BaseInlineFormSet
    Add ext_data support for __init__.
    """

    def __init__(self, *args, **kwargs):
        self.ext_params = {}
        if 'ext_data' in kwargs:
            self.ext_params['ext_data'] = kwargs.pop('ext_data')
        super(LBBaseInlineFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        kwargs.update(self.ext_params)
        return super(LBBaseInlineFormSet, self)._construct_form(i, **kwargs)


def row_div(fnames, span=4, hidden_fields=[]):
    divs = []
    for fname in fnames:
        if fname in hidden_fields:
            continue
        if isinstance(fname, PrependedText) and fname.field in hidden_fields:
            continue
        divs.append(
            Div(fname, css_class='col-md-%s form-group' % span),
        )
    return Div(*divs, css_class='row')
