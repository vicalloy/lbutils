from django import forms
from lbutils import (BootstrapFormHelperMixin, JustSelectedSelect,
                     JustSelectedSelectMultiple)

from .models import Book


class BookForm(BootstrapFormHelperMixin, forms.ModelForm):
    def __init__(self, *args, **kw):
        super(BookForm, self).__init__(*args, **kw)
        self.init_crispy_helper()

    def clean_name(self):
        name = self.cleaned_data.get('name')
        self.check_uniqe(Book, name=name)
        return name

    class Meta:
        model = Book
        fields = [
            'name', 'descn', 'price', 'is_active', 'category', 'authors'
        ]
        widgets = {
            'category': JustSelectedSelect,
            'authors': JustSelectedSelectMultiple
        }
