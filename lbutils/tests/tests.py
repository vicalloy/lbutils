from __future__ import unicode_literals


from unittest import skipUnless
import django
from django.test import TestCase

from lbutils import fmt_month
from lbutils import get_year_choices
from lbutils import fmt_num
from lbutils import create_instance
from lbutils import get_or_none
from lbutils import get_pk_or_none
from lbutils import get_sum
from lbutils import get_max
from lbutils import do_filter
from lbutils import QuickSearchForm

from .models import Book
from .models import Category
from .forms import BookForm


class DateUtilsTests(TestCase):
    def test_fmt_month(self):
        self.assertEqual('01', fmt_month('1'))
        self.assertEqual('12', fmt_month('12'))

    def test_get_year_choices(self):
        choices = get_year_choices()
        self.assertTrue(choices[0][0])
        choices = get_year_choices(blank_label='------')
        self.assertEqual('', choices[0][0])


class UtilsTests(TestCase):
    def test_fmt_num(self):
        self.assertEqual('9,000,000', fmt_num(9000000))

    def test_create_instance(self):
        d = create_instance('datetime.datetime', year=2000, month=2, day=1)
        self.assertEqual('2000-02-01', d.strftime('%Y-%m-%d'))


class QSTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name='category')
        Book.objects.create(
            category=category, name='book-01',
            price=100,
            descn='descn')
        Book.objects.create(
            category=category, name='book-02',
            price=200,
            descn='descn')
        Book.objects.create(
            name='book-03',
            is_active=False,
            descn='descn')

    def test_get_or_none(self):
        self.assertEqual(None, get_or_none(Book, name='not exist'))
        self.assertEqual(
            'book-01',
            get_or_none(Book, name='book-01').name)

    def test_get_pk_or_none(self):
        self.assertEqual(None, get_pk_or_none(Book, name='not exist'))
        self.assertEqual(
            Book.objects.get(name='book-01').pk,
            get_pk_or_none(Book, name='book-01'))

    def test_get_sum(self):
        qs = Book.objects.all()
        self.assertEqual(300, get_sum(qs, 'price'))
        qs = Book.objects.filter(name='book-01')
        self.assertEqual(100, get_sum(qs, 'price'))

    def test_get_max(self):
        qs = Book.objects.all()
        self.assertEqual(200, get_max(qs, 'price'))

    def test_do_filter_quick_query_fields(self):
        books = Book.objects.all()
        qdata = {'q_quick_search_kw': ''}
        qs = do_filter(books, qdata, ['name', 'category__name'])
        self.assertEqual(3, qs.count())
        qdata = {'q_quick_search_kw': '01'}
        qs = do_filter(books, qdata, ['name', 'category__name'])
        self.assertEqual(1, qs.count())
        qdata = {'q_quick_search_kw': 'xxxxx'}
        qs = do_filter(books, qdata, ['name', 'category__name'])
        self.assertEqual(0, qs.count())
        qdata = {'q_quick_search_kw': 'catego'}
        qs = do_filter(books, qdata, ['name', 'category__name'])
        self.assertEqual(2, qs.count())

    def test_do_filter_int_quick_query_fields(self):
        books = Book.objects.all()
        qdata = {'q_quick_search_kw': '100'}
        qs = do_filter(books, qdata, ['name', 'category__name'], int_quick_query_fields=['price'])
        self.assertEqual(1, qs.count())

    def test_do_filter(self):
        books = Book.objects.all()
        qdata = {'q__price': '100'}
        qs = do_filter(books, qdata)
        self.assertEqual(1, qs.count())
        qdata = {'q__name__icontains': 'book-03'}
        qs = do_filter(books, qdata)
        self.assertEqual(1, qs.count())
        qdata = {'q__category__name__icontains': 'catego'}
        qs = do_filter(books, qdata)
        self.assertEqual(2, qs.count())
        qdata = {'q__is_active': '__False'}
        qs = do_filter(books, qdata)
        self.assertEqual(1, qs.count())


class FormTests(TestCase):
    def setUp(self):
        data = {'name': 'book name'}
        self.form = BookForm(data)

    @skipUnless(django.VERSION < (1, 10, 0), "crispy_forms not support Django 1.10")
    def test_quicksearchform(self):
        from crispy_forms.templatetags.crispy_forms_filters import as_crispy_form
        data = {'q_quick_search_kw': 'keyword'}
        form = QuickSearchForm(data)
        form.is_valid()
        self.assertEqual('keyword', form.cleaned_data['q_quick_search_kw'])
        self.assertTrue('id_q_quick_search_kw' in as_crispy_form(form))

    def test_filter_fields(self):
        # filter_fields(self, fields=[], exclude=[], include_all_if_empty=True):
        field_names = ['name', 'descn']
        fields = self.form.filter_fields(field_names)
        self.assertEqual(field_names, [e.name for e in fields])
        fields = self.form.filter_fields(exclude=field_names)
        self.assertEqual(['price', 'is_active', 'category'], [e.name for e in fields])
        fields = self.form.filter_fields(include_all_if_empty=True)
        self.assertEqual(['name', 'descn', 'price', 'is_active', 'category'], [e.name for e in fields])
        fields = self.form.filter_fields(include_all_if_empty=False)
        self.assertEqual([], [e.name for e in fields])

    def test_init_crispy_helper(self):
        self.form.init_crispy_helper()
        self.assertTrue(self.form.helper is not None)

    @skipUnless(django.VERSION >= (1, 7, 0), "test only applies to Django 1.7+")
    def test_errors_as_text(self):
        data = {}
        form = BookForm(data)
        form.is_valid()
        self.assertTrue('Name' in form.errors_as_text())

    def test_as_text_fields(self):
        self.form.as_text_fields(include_all_if_empty=True)
        self.assertTrue("<span class='text-value'>book name</span>" in self.form.as_table())

    def test_as_hidden_fields(self):
        self.form.as_hidden_fields(include_all_if_empty=True)
        self.assertTrue('<input id="id_name" name="name" type="hidden" value="book name" />' in self.form.as_table())

    def test_add_attr2fields(self):
        self.form.add_attr2fields('fn', 'fx1')
        self.assertTrue('fn="fx1"' in self.form.as_table())
        self.form.add_attr2fields('fn', 'fx2')
        self.assertTrue('fn="fx1 fx2"' in self.form.as_table())

    def test_as_required_fields(self):
        data = {'name': 'book name'}
        form = BookForm(data)
        self.form.is_valid()
        self.assertTrue('errorlist' not in form.as_table())
        form = BookForm(data)
        self.form.as_required_fields(['descn'])
        self.form.is_valid()
        self.assertTrue('errorlist' not in form.as_table())

    def test_check_uniqe(self):
        pass
