# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.forms.formsets import BaseFormSet
from django.forms.models import BaseModelFormSet
from django.forms.models import BaseInlineFormSet
from crispy_forms.bootstrap import PrependedText
from django.utils.translation import ugettext_lazy as _

try:
    from crispy_forms.helper import FormHelper
    from crispy_forms.layout import Layout
    from crispy_forms.bootstrap import StrictButton
    from crispy_forms.layout import Div
except ImportError:
    pass

from .widgets import JustSelectedSelectMultiple
from .widgets import TextWidget


class FormHelperMixin(object):

    def init_crispy_helper(self):
        self.helper = helper = FormHelper()
        helper.label_class = 'col-xs-2'
        helper.field_class = 'col-xs-8'
        helper.form_tag = False
        return helper

    def errors_as_text(self):
        errors = []
        errors.append(self.non_field_errors().as_text())
        errors_data = self.errors.as_data()
        for key, value in errors_data.items():
            field_label = self.fields[key].label
            err_descn = ''.join([unicode(e.message) for e in value])
            error = "%s %s" % (field_label, err_descn)
            errors.append(error)
        return ','.join(errors)

    def as_param_ext_val(self, field_name, param_field_id, val_name):
        self.add_class2fields('from-param-ext', fields=[field_name])
        self.add_attr2fields('param-field', param_field_id, fields=[field_name])
        self.add_attr2fields('val-name', val_name, fields=[field_name])

    def as_readonly_fields(self, fields=[], exclude=[]):
        if not (fields or exclude):
            return
        self.add_attr2fields(
            'readonly', 'readonly',
            fields=fields, exclude=exclude)

    def as_text_fields(self, fields=[], exclude=[], include_all_if_empty=True):
        if not (fields or exclude):
            return
        for f in self.filter_fields(self, fields, exclude, include_all_if_empty):
            f = self.fields[f.name]
            f.widget = TextWidget(src_widget=f.widget)

    def as_hidden_fields(self, fields=[], exclude=[], include_all_if_empty=True):
        if not (fields or exclude):
            return
        for f in self.filter_fields(self, fields, exclude, include_all_if_empty):
            f = self.fields[f.name]
            f.required = False
            if isinstance(f.widget, (forms.SelectMultiple, JustSelectedSelectMultiple)):
                f.widget = forms.MultipleHiddenInput()
            else:
                f.widget = forms.HiddenInput()

    def as_sub_param_field(self, field_name, parent_field_id, param_code):
        self.add_class2fields('ajax-sub-param', fields=[field_name])
        self.add_attr2fields('parent-field', parent_field_id, fields=[field_name])
        self.add_attr2fields('param-code', param_code, fields=[field_name])

    def add_select_component(self, fields=[], exclude=[], include_all_if_empty=True):
        """
        为widget为select的字段添加 class select_component （选择组件样式）
        :fields 需要包含的段名，为空表示所有
        :exclude 需要排除的字段名
        """
        attr_name = 'class'
        attr_val = 'select_component'
        for f in self.filter_fields(fields, exclude, include_all_if_empty):
            f = self.fields[f.name]
            if isinstance(f.widget, forms.Select):
                org_val = f.widget.attrs.get(attr_name, '')
                f.widget.attrs[attr_name] = '%s %s' % (org_val, attr_val) if org_val else attr_val

    def add_attr2fields(self, attr_name, attr_val, fields=[], exclude=[], include_all_if_empty=True):
        """
        为form字段增加attr
        :attr_name 需要添加的attr名称
        :attr_val 需要添加的值
        :fields 需要包含的段名，为空表示所有
        :exclude 需要排除的字段名
        """
        for f in self.filter_fields(self, fields, exclude, include_all_if_empty):
            f = self.fields[f.name]
            org_val = f.widget.attrs.get(attr_name, '')
            f.widget.attrs[attr_name] = '%s %s' % (org_val, attr_val) if org_val else attr_val

    def add_class2fields(self, html_class, fields=[], exclude=[], include_all_if_empty=True):
        """
        为form字段增加class
        :html_class 需要添加的class
        :fields 需要添加class的段名，为空表示所有
        :exclude 需要排除的字段名
        """
        self.add_attr2fields('class', html_class, fields, exclude)

    def filter_fields(form, fields=[], exclude=[], include_all_if_empty=True):
        """
        filter fields
        :fields
        :exclude
        :include_all_if_empty if fields is empty return all fields
        @return 字段列表
        """
        if not include_all_if_empty and not fields:
            return []
        ret = []
        for f in form.visible_fields():
            if fields and f.name not in fields:
                continue
            if exclude and f.name in exclude:
                continue
            ret.append(f)
        return ret

    def set_required_fields(self, fields=[]):
        fields = self.filter_fields(fields)
        for f in fields:
            f = self.fields[f.name]
            f.required = True

    def check_uniqe(self, obj_class, error_msg=_('Must be unique'), **kwargs):
        if obj_class.objects.filter(**kwargs).exclude(pk=self.instance.pk):
            raise forms.ValidationError(error_msg)

    def row_div(self, fnames, span=4):
        fields = self.filter_fields(fnames)
        fnames = [e.name for e in fields if not e.is_hidden]
        return row_div(fnames, span=span)


class QuickSearchForm(FormHelperMixin, forms.Form):
    q_quick_search_kw = forms.CharField(label="关键字", required=False)

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


def add_empty_form_plus_for_fs(formset, **kwargs):
    formset.empty_form_plus = formset.form(
        auto_id=formset.auto_id,
        empty_permitted=True,
        prefix=formset.add_prefix('__prefix__'), **kwargs)
    formset.add_fields(formset.empty_form_plus, None)


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
