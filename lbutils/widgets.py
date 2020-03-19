from django.forms import (HiddenInput, MultipleHiddenInput, Select,
                          SelectMultiple)
from django.forms.models import ModelChoiceIterator
from django.forms.widgets import CheckboxInput, Textarea, Widget
from django.utils.encoding import force_text

__all__ = (
    'JustSelectedSelect', 'JustSelectedSelectMultiple', 'TextWidget',
)


class JustSelectedMixin(object):
    """ only generate selected option """

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

    def get_only_selected_choices(self, value):
        """Return a list of optgroups for this widget."""
        schoices = self.choices
        selected_choices = set([force_text(v) for v in value if v])
        if isinstance(schoices, ModelChoiceIterator):
            schoices.queryset = schoices.queryset.filter(pk__in=selected_choices)
        else:
            schoices = [e for e in schoices if force_text(e) in selected_choices]
        return schoices


class JustSelectedSelect(JustSelectedMixin, Select):
    def optgroups(self, name, value, attrs=None):
        self.choices = self.get_only_selected_choices(value)
        return super(JustSelectedSelect, self).optgroups(name, value, attrs)

    def render_options(self, selected_choices):
        self.choices = self.get_only_selected_choices(selected_choices)
        return super(JustSelectedSelect, self).render_options(selected_choices)


class JustSelectedSelectMultiple(JustSelectedMixin, SelectMultiple):
    """ only generate selected option """

    def optgroups(self, name, value, attrs=None):
        self.choices = self.get_only_selected_choices(value)
        return super(JustSelectedSelectMultiple, self).optgroups(name, value, attrs)

    def render_options(self, selected_choices):
        self.choices = self.get_only_selected_choices(selected_choices)
        return super(JustSelectedSelectMultiple, self).render_options(selected_choices)


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

    def render(self, name, value, attrs=None, renderer=None):
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
