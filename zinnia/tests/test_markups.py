"""Test cases for Zinnia's markups"""
import sys
import warnings
from unittest import skipUnless
try:
    import builtins
except ImportError:  # Python 2
    import __builtin__ as builtins

from django.test import TestCase

from zinnia import markups
from zinnia.markups import html_format
from zinnia.markups import markdown
from zinnia.markups import restructuredtext
from zinnia.markups import textile
from zinnia.tests.utils import is_lib_available


class MarkupsTestCase(TestCase):
    text = 'Hello *World* !'

    @skipUnless(is_lib_available('textile'), 'Textile is not available')
    def test_textile(self):
        self.assertEqual(textile(self.text).strip(),
                         '<p>Hello <strong>World</strong> !</p>')

    @skipUnless(is_lib_available('markdown'), 'Markdown is not available')
    def test_markdown(self):
        self.assertEqual(markdown(self.text).strip(),
                         '<p>Hello <em>World</em> !</p>')

    @skipUnless(is_lib_available('markdown'), 'Markdown is not available')
    def test_markdown_extensions(self):
        text = '[TOC]\n\n# Header 1\n\n## Header 2'
        self.assertEqual(markdown(text).strip(),
                         '<p>[TOC]</p>\n<h1>Header 1</h1>'
                         '\n<h2>Header 2</h2>')
        self.assertEqual(
            markdown(text, extensions=['markdown.extensions.toc']).strip(),
            '<div class="toc">\n<ul>\n<li><a href="#header-1">'
            'Header 1</a><ul>\n<li><a href="#header-2">'
            'Header 2</a></li>\n</ul>\n</li>\n</ul>\n</div>'
            '\n<h1 id="header-1">Header 1</h1>\n'
            '<h2 id="header-2">Header 2</h2>')
        from markdown.extensions.toc import TocExtension
        tocext = TocExtension(marker='--TOC--', permalink='PL')
        self.assertEqual(markdown(text, extensions=[tocext]).strip(),
                         '<p>[TOC]</p>\n<h1 id="header-1">Header 1'
                         '<a class="headerlink" href="#header-1" '
                         'title="Permanent link">PL</a></h1>\n'
                         '<h2 id="header-2">Header 2'
                         '<a class="headerlink" href="#header-2" '
                         'title="Permanent link">PL</a></h2>')

    @skipUnless(is_lib_available('docutils'), 'Docutils is not available')
    def test_restructuredtext(self):
        self.assertEqual(restructuredtext(self.text).strip(),
                         '<p>Hello <em>World</em> !</p>')

    @skipUnless(is_lib_available('docutils'), 'Docutils is not available')
    def test_restructuredtext_settings_override(self):
        text = 'My email is toto@example.com'
        self.assertEqual(restructuredtext(text).strip(),
                         '<p>My email is <a class="reference external" '
                         'href="mailto:toto&#64;example.com">'
                         'toto&#64;example.com</a></p>')
        self.assertEqual(
            restructuredtext(text, {'cloak_email_addresses': True}).strip(),
            '<p>My email is <a class="reference external" '
            'href="mailto:toto&#37;&#52;&#48;example&#46;com">'
            'toto<span>&#64;</span>example<span>&#46;</span>com</a></p>')


@skipUnless(sys.version_info >= (2, 7, 0),
            'Cannot run these tests under Python 2.7')
class MarkupFailImportTestCase(TestCase):
    exclude_list = ['textile', 'markdown', 'docutils']

    def setUp(self):
        self.original_import = builtins.__import__
        builtins.__import__ = self.import_hook

    def tearDown(self):
        builtins.__import__ = self.original_import

    def import_hook(self, name, *args, **kwargs):
        if name in self.exclude_list:
            raise ImportError('%s module has been disabled' % name)
        else:
            self.original_import(name, *args, **kwargs)

    def test_textile(self):
        with warnings.catch_warnings(record=True) as w:
            result = textile('My *text*')
        self.tearDown()
        self.assertEqual(result, 'My *text*')
        self.assertTrue(issubclass(w[-1].category, RuntimeWarning))
        self.assertEqual(
            str(w[-1].message),
            "The Python textile library isn't installed.")

    def test_markdown(self):
        with warnings.catch_warnings(record=True) as w:
            result = markdown('My *text*')
        self.tearDown()
        self.assertEqual(result, 'My *text*')
        self.assertTrue(issubclass(w[-1].category, RuntimeWarning))
        self.assertEqual(
            str(w[-1].message),
            "The Python markdown library isn't installed.")

    def test_restructuredtext(self):
        with warnings.catch_warnings(record=True) as w:
            result = restructuredtext('My *text*')
        self.tearDown()
        self.assertEqual(result, 'My *text*')
        self.assertTrue(issubclass(w[-1].category, RuntimeWarning))
        self.assertEqual(
            str(w[-1].message),
            "The Python docutils library isn't installed.")


class HtmlFormatTestCase(TestCase):

    def setUp(self):
        self.original_rendering = markups.MARKUP_LANGUAGE

    def tearDown(self):
        markups.MARKUP_LANGUAGE = self.original_rendering

    def test_html_format_default(self):
        markups.MARKUP_LANGUAGE = None
        self.assertEquals(html_format(''), '')
        self.assertEquals(html_format('Content'), '<p>Content</p>')
        self.assertEquals(html_format('Content</p>'), 'Content</p>')
        self.assertEquals(html_format('Hello\nworld!'),
                          '<p>Hello<br />world!</p>')

    @skipUnless(is_lib_available('textile'), 'Textile is not available')
    def test_html_content_textitle(self):
        markups.MARKUP_LANGUAGE = 'textile'
        value = 'Hello world !\n\n' \
                'this is my content :\n\n' \
                '* Item 1\n* Item 2'
        self.assertEqual(html_format(value),
                         '\t<p>Hello world !</p>\n\n\t'
                         '<p>this is my content :</p>\n\n\t'
                         '<ul>\n\t\t<li>Item 1</li>\n\t\t'
                         '<li>Item 2</li>\n\t</ul>')

    @skipUnless(is_lib_available('markdown'), 'Markdown is not available')
    def test_html_content_markdown(self):
        markups.MARKUP_LANGUAGE = 'markdown'
        value = 'Hello world !\n\n' \
                'this is my content :\n\n' \
                '* Item 1\n* Item 2'
        self.assertEqual(html_format(value),
                         '<p>Hello world !</p>\n'
                         '<p>this is my content :</p>'
                         '\n<ul>\n<li>Item 1</li>\n'
                         '<li>Item 2</li>\n</ul>')

    @skipUnless(is_lib_available('docutils'), 'Docutils is not available')
    def test_html_content_restructuredtext(self):
        markups.MARKUP_LANGUAGE = 'restructuredtext'
        value = 'Hello world !\n\n' \
                'this is my content :\n\n' \
                '* Item 1\n* Item 2'
        self.assertEqual(html_format(value),
                         '<p>Hello world !</p>\n'
                         '<p>this is my content :</p>'
                         '\n<ul class="simple">\n<li>Item 1</li>\n'
                         '<li>Item 2</li>\n</ul>\n')
