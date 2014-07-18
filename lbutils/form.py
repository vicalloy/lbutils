# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from itertools import chain
from django.utils.encoding import force_unicode
from django.forms.models import ModelChoiceIterator
from django.utils.html import escape
from django.forms.util import flatatt
from django.utils.safestring import mark_safe
from django.utils.datastructures import MultiValueDict, MergeDict
from django.forms import Select
from django.forms.formsets import BaseFormSet
from django.forms.models import BaseModelFormSet
from django.forms.models import BaseInlineFormSet


def forms_is_valid(forms):
    is_valid = True
    for form in forms:
        is_valid = is_valid and form.is_valid()
    return is_valid


class JustSelectedSelect(Select):

    def render_options(self, choices, selected_choices):
        selected_choices = set([force_unicode(v) for v in selected_choices if v])
        output = []
        schoices = self.choices
        if isinstance(schoices, ModelChoiceIterator):
            schoices.queryset = schoices.queryset.filter(pk__in=selected_choices)
        if isinstance(choices, ModelChoiceIterator):
            choices.queryset = choices.queryset.filter(pk__in=selected_choices)
        for option_value, option_label in chain(schoices, choices):
            if isinstance(option_label, (list, tuple)):
                output.append(u'<optgroup label="%s">' % escape(force_unicode(option_value)))
                for option in option_label:
                    if not force_unicode([0]) in selected_choices:
                        continue
                    output.append(self.render_option(selected_choices, *option))
                output.append(u'</optgroup>')
            else:
                if not force_unicode(option_value) in selected_choices:
                    continue
                output.append(self.render_option(selected_choices, option_value, option_label))
        return u'\n'.join(output)


class JustSelectedSelectMultiple(JustSelectedSelect):
    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<select multiple="multiple"%s>' % flatatt(final_attrs)]
        options = self.render_options(choices, value)
        if options:
            output.append(options)
        output.append('</select>')
        return mark_safe(u'\n'.join(output))

    def value_from_datadict(self, data, files, name):
        if isinstance(data, (MultiValueDict, MergeDict)):
            return data.getlist(name)
        return data.get(name, None)

    def _has_changed(self, initial, data):
        if initial is None:
            initial = []
        if data is None:
            data = []
        if len(initial) != len(data):
            return True
        initial_set = set([force_unicode(value) for value in initial])
        data_set = set([force_unicode(value) for value in data])
        return data_set != initial_set


class LBBaseFormSet(BaseFormSet):

    def __init__(self, *args, **kwargs):
        self.ext_params = {}
        if 'ext_data' in kwargs:
            self.ext_params['ext_data'] = kwargs.pop('ext_data')
        super(LBBaseFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        kwargs.update(self.ext_params)
        return super(LBBaseFormSet, self)._construct_form(i, **kwargs)


class LBBaseModelFormSet(BaseModelFormSet):

    def __init__(self, *args, **kwargs):
        self.ext_params = {}
        if 'ext_data' in kwargs:
            self.ext_params['ext_data'] = kwargs.pop('ext_data')
        super(LBBaseModelFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        kwargs.update(self.ext_params)
        return super(LBBaseModelFormSet, self)._construct_form(i, **kwargs)


class LBBaseInlineFormSet(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        self.ext_params = {}
        if 'ext_data' in kwargs:
            self.ext_params['ext_data'] = kwargs.pop('ext_data')
        super(LBBaseInlineFormSet, self).__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        kwargs.update(self.ext_params)
        return super(LBBaseInlineFormSet, self)._construct_form(i, **kwargs)
