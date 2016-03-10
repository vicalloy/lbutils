# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from itertools import chain
import django
from django.utils.encoding import force_text
from django.forms.models import ModelChoiceIterator
from django.utils.html import escape
try:
    from django.forms.util import flatatt
except ImportError:  # Django >= 1.9
    from django.forms.utils import flatatt
from django.utils.safestring import mark_safe
from django.utils.datastructures import MultiValueDict
if django.VERSION < (1, 9):
    from django.utils.datastructures import MergeDict
from django.forms import Select
from django.forms import MultipleHiddenInput, HiddenInput
from django.forms.widgets import Widget, Textarea, CheckboxInput

__all__ = (
    'JustSelectedSelect', 'JustSelectedSelectMultiple', 'TextWidget',
)


class JustSelectedSelect(Select):
    """ only generate selected option """

    def render_options(self, choices, selected_choices):
        # Normalize to strings.
        # FIXME selected value couldn't be ‘’ None
        selected_choices = set([force_text(v) for v in selected_choices if v])
        output = []
        schoices = self.choices
        if isinstance(schoices, ModelChoiceIterator):
            schoices.queryset = schoices.queryset.filter(pk__in=selected_choices)
        if isinstance(choices, ModelChoiceIterator):
            choices.queryset = choices.queryset.filter(pk__in=selected_choices)
        for option_value, option_label in chain(schoices, choices):
            if isinstance(option_label, (list, tuple)):
                output.append(u'<optgroup label="%s">' % escape(force_text(option_value)))
                for option in option_label:
                    if not force_text([0]) in selected_choices:
                        continue
                    output.append(self.render_option(selected_choices, *option))
                output.append(u'</optgroup>')
            else:
                if not force_text(option_value) in selected_choices:
                    continue
                output.append(self.render_option(selected_choices, option_value, option_label))
        return u'\n'.join(output)

    def render_readonly(self, name, value, attrs):
        schoices = self.choices
        if isinstance(schoices, ModelChoiceIterator):
            if isinstance(value, list):
                schoices.queryset = schoices.queryset.filter(pk__in=value)
            else:
                schoices.queryset = schoices.queryset.filter(pk=value)
        for o in schoices:
            if "%s" % o[0] == "%s" % value:
                return o[1]
        return ""


class JustSelectedSelectMultiple(JustSelectedSelect):
    """ only generate selected option """

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
        cls_tuple = (MultiValueDict, )
        if django.VERSION < (1, 9):
            cls_tuple = (MultiValueDict, MergeDict, )
        if isinstance(data, cls_tuple):
            return data.getlist(name)
        return data.get(name, None)

    def _has_changed(self, initial, data):
        if initial is None:
            initial = []
        if data is None:
            data = []
        if len(initial) != len(data):
            return True
        initial_set = set([force_text(value) for value in initial])
        data_set = set([force_text(value) for value in data])
        return data_set != initial_set


def render_hidden(name, value):
    """ render as hidden widget """
    if isinstance(value, list):
        return MultipleHiddenInput().render(name, value)
    return HiddenInput().render(name, value)


class TextWidget(Widget):
    """ render as text """

    def __init__(self, attrs=None, src_widget=None):
        super(TextWidget, self).__init__(attrs)
        self.src_widget = src_widget

    def gen_output(self, descn, value, name):
        return "<span class='text-value'>%s</span> %s" % (descn, render_hidden(name, value))

    def value_from_datadict(self, data, files, name):
        return self.src_widget.value_from_datadict(data, files, name)

    def render(self, name, value, attrs=None):
        func_render_readonly = getattr(self.src_widget, 'render_readonly', None)
        if func_render_readonly:
            descn = func_render_readonly(name, value, attrs)
            return self.gen_output(descn, value, name)
        if isinstance(self.src_widget, Select):
            if isinstance(value, list):
                values = ["%s" % e for e in value]
            else:
                values = ["%s" % value]
            descns = []
            for v, descn in self.src_widget.choices:
                if "%s" % v in values:
                    descns.append(descn)
            return self.gen_output(','.join(descns), value, name)
        if isinstance(self.src_widget, CheckboxInput):
            descn = u'√' if value else u'×'
            return self.gen_output(descn, value, name)
        descn = '' if value is None else '%s' % value
        # TODO if in pre element
        if isinstance(self.src_widget, Textarea):
            descn = value
        return self.gen_output(descn, value, name)
