# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from lbutils import FormHelperMixin
from .models import Book


class BookForm(FormHelperMixin, forms.ModelForm):
    def __init__(self, *args, **kw):
        super(BookForm, self).__init__(*args, **kw)
        self.init_crispy_helper()

    class Meta:
        model = Book
        fields = [
            'name', 'descn', 'price', 'is_active', 'category'
        ]
