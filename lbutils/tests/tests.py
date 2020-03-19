from unittest import skipUnless

import django
from django.http import QueryDict
from django.test import TestCase
from lbutils import (QuickSearchForm, create_instance, do_filter, fmt_month,
                     fmt_num, format_filesize, forms_is_valid, get_max,
                     get_or_none, get_pk_or_none, get_sum, get_year_choices,
                     qdict_get_list, render_json, simple_export2xlsx)
from lbutils.templatetags.lbutils import display_array, get_setting

from .forms import BookForm
from .models import Author, Book, Category


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

    def test_format_filesize(self):
        self.assertEqual('40 B', format_filesize(40))
        self.assertEqual('3.91 KB', format_filesize(4000))
        self.assertEqual('3.81 MB', format_filesize(4000000))


def create_books():
    category = Category.objects.create(name='category-01')
    Category.objects.create(name='category-02')
    author1 = Author.objects.create(name='author-01')
    author2 = Author.objects.create(name='author-02')
    Author.objects.create(name='author-03')
    book = Book.objects.create(
        category=category, name='book-01',
        price=100,
        descn='descn')
    book.authors.set([author1, author2])
    Book.objects.create(
        category=category, name='book-02',
        price=200,
        descn='descn')
    Book.objects.create(
        name='book-03',
        is_active=False,
        descn='descn')
    return Book.objects.all()


class QSTests(TestCase):
    def setUp(self):
        create_books()

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
        qdata = {'q_quick_search_kw': 'ook-01'}
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
        qdata = {'q__name__icontains': 'ook-02,ook-03'}
        qs = do_filter(books, qdata)
        self.assertEqual(2, qs.count())
        qdata = {'q__name__in': 'book-02,book-03'}
        qs = do_filter(books, qdata)
        self.assertEqual(2, qs.count())
        qdata = {'q__category__name__icontains': 'catego'}
        qs = do_filter(books, qdata)
        self.assertEqual(2, qs.count())
        qdata = {'q__is_active': '__False'}
        qs = do_filter(books, qdata)
        self.assertEqual(1, qs.count())
        # sql: select * from table where field1>field2
        qdata = {'q__name__gt': 'F__name'}
        qs = do_filter(books, qdata)
        self.assertEqual(0, qs.count())


@skipUnless(django.VERSION >= (1, 10, 0), "JustSelected* only support Django >= 1.10")
class FormTests(TestCase):
    def setUp(self):
        create_books()
        data = {'name': 'book name'}
        self.form = BookForm(data)
        self.edit_form = BookForm(
            instance=Book.objects.get(name='book-01'))

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
        self.assertEqual(['price', 'is_active', 'category', 'authors'], [e.name for e in fields])
        fields = self.form.filter_fields(include_all_if_empty=True)
        self.assertEqual(['name', 'descn', 'price', 'is_active', 'category', 'authors'], [e.name for e in fields])
        fields = self.form.filter_fields(include_all_if_empty=False)
        self.assertEqual([], [e.name for e in fields])

    def test_init_crispy_helper(self):
        self.form.init_crispy_helper()
        self.assertTrue(self.form.helper is not None)

    def test_layout_fields(self):
        self.form.init_crispy_helper()
        self.form.layout_fields([
            ('name', 'price'),
            ('descn', ),
        ])

    @skipUnless(django.VERSION >= (1, 7, 0), "test only applies to Django 1.7+")
    def test_errors_as_text(self):
        data = {}
        form = BookForm(data)
        form.is_valid()
        self.assertTrue('Name' in form.errors_as_text())

    def test_as_text_fields(self):
        self.edit_form.as_text_fields(include_all_if_empty=True)
        self.assertTrue("<span class='text-value'>book-01</span>" in self.edit_form.as_table())

    def test_as_hidden_fields(self):
        self.form.as_hidden_fields(include_all_if_empty=True)
        self.assertTrue('hidden' in self.form.as_table())

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
        book = Book.objects.create(
            name='book-0x',
            price=100,
            descn='descn')
        # existed
        data = {'name': 'book-0x'}
        form = BookForm(data)
        form.is_valid()
        self.assertTrue('errorlist' in form.as_table())
        # edit object
        form = BookForm(data, instance=book)
        form.is_valid()
        self.assertTrue('errorlist' not in form.as_table())
        # not existed
        form = BookForm({'name': 'new book'}, instance=book)
        form.is_valid()
        self.assertTrue('errorlist' not in form.as_table())

    def test_row_div(self):
        self.form.row_div(['name', 'price'], 6)

    def test_just_selected_widgets(self):
        html = self.edit_form.as_table()
        self.assertTrue('category-01' in html)
        self.assertTrue('category-02' not in html)
        self.assertTrue('author-01' in html)
        self.assertTrue('author-02' in html)
        self.assertTrue('author-03' not in html)


class FormSetTests(TestCase):
    pass


class ViewsTests(TestCase):
    def test_forms_is_valid(self):
        sform = QuickSearchForm({})
        bform = BookForm({})
        forms = [sform, bform]
        self.assertFalse(forms_is_valid(forms))
        bform = BookForm({'name': 'ok'})
        forms = [sform, bform]
        self.assertTrue(forms_is_valid(forms))

    def test_render_json(self):
        data = {'name': 'name 中文'}
        out = render_json(data).content
        self.assertEqual(
            b'{"name": "name \xe4\xb8\xad\xe6\x96\x87"}', out)
        # TODO jsonp

    def test_qdict_get_list(self):
        data = QueryDict('a=1&a=2&a=')
        self.assertTrue('' not in qdict_get_list(data, 'a'))


class TagsTests(TestCase):
    def test_display_array(self):
        self.assertEqual('1, 2, 3', display_array(['1', '2', '3']))

    def test_get_setting(self):
        ctx = {}
        v = get_setting(ctx, key='GET_SETTING', default_val="", as_key=None)
        self.assertEqual('ABC', v)
        get_setting(ctx, key='GET_SETTING', default_val="", as_key='new')
        self.assertEqual('ABC', ctx['new'])
        v = get_setting(ctx, key='GET_NOT_EXIST', default_val="DEFAULT", as_key=None)
        self.assertEqual('DEFAULT', v)


class XlsxUtilsTests(TestCase):
    def test_simple_export2xlsx(self):
        def func_data(o):
            return [
                o.name,
                o.price
            ]
        qs = Book.objects.all()
        titles = ['name', 'price']
        response = simple_export2xlsx('fn.xlsx', titles, qs, func_data)
        self.assertTrue(response is not None)
