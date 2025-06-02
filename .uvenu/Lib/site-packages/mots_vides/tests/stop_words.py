"""
Tests for StopWord
"""
import os
import sys
from unittest import TestCase

from mots_vides.stop_words import StopWord
from mots_vides.factory import StopWordFactory


class StopWordTestCase(TestCase):

    def setUp(self):
        self.sw = StopWord('foo', ['foo', 'bar', 'baz'])

    def test_len(self):
        self.assertEqual(len(self.sw), 3)

    def test_contains(self):
        self.assertTrue('foo' in self.sw)
        self.assertFalse('qux' in self.sw)

    def test_iter(self):
        self.assertEqual(len(list(self.sw)), 3)

    def test_add(self):
        nsw = StopWord('bar', ['baz', 'qux', 'norf'])
        nsw = nsw + self.sw
        self.assertEqual(sorted(list(nsw)),
                         ['bar', 'baz', 'foo', 'norf', 'qux'])
        self.assertEqual(nsw.language, 'bar')

        nsw = StopWord('bar', ['baz', 'qux', 'norf'])
        nsw += self.sw
        self.assertEqual(sorted(list(nsw)),
                         ['bar', 'baz', 'foo', 'norf', 'qux'])
        self.assertEqual(nsw.language, 'bar')

        nsw = StopWord('bar', ['baz', 'qux', 'norf'])
        nsw += ['tic', 'tac', 'toc']
        self.assertEqual(sorted(list(nsw)),
                         ['baz', 'norf', 'qux', 'tac', 'tic', 'toc'])

        nsw = StopWord('bar', ['baz', 'qux', 'norf'])
        nsw += 'tic'
        self.assertEqual(sorted(list(nsw)),
                         ['baz', 'norf', 'qux', 'tic'])

        if sys.version_info[0] == 2:
            nsw = StopWord('bar', ['baz', 'qux', 'norf'])
            nsw += 'tic'.decode('utf-8')
            self.assertEqual(sorted(list(nsw)),
                             ['baz', 'norf', 'qux', 'tic'])

        nsw = StopWord('bar', ['baz', 'qux', 'norf'])
        self.assertRaises(TypeError, nsw.__add__, object())
        self.assertEqual(sorted(list(nsw)),
                         ['baz', 'norf', 'qux'])

    def test_sub(self):
        nsw = StopWord('bar', ['baz', 'qux', 'norf'])
        nsw = nsw - self.sw
        self.assertEqual(sorted(list(nsw)), ['norf', 'qux'])
        self.assertEqual(nsw.language, 'bar')

        nsw = StopWord('bar', ['baz', 'qux', 'norf'])
        nsw -= self.sw
        self.assertEqual(sorted(list(nsw)), ['norf', 'qux'])
        self.assertEqual(nsw.language, 'bar')

        nsw = StopWord('bar', ['baz', 'qux', 'norf'])
        nsw -= ['tic', 'tac', 'toc', 'qux']
        self.assertEqual(sorted(list(nsw)),
                         ['baz', 'norf'])

        nsw = StopWord('bar', ['baz', 'qux', 'norf'])
        nsw -= 'baz'
        self.assertEqual(sorted(list(nsw)),
                         ['norf', 'qux'])

        if sys.version_info[0] == 2:
            nsw = StopWord('bar', ['baz', 'qux', 'norf'])
            nsw -= 'baz'.decode('utf-8')
            self.assertEqual(sorted(list(nsw)),
                             ['norf', 'qux'])

        nsw = StopWord('bar', ['baz', 'qux', 'norf'])
        self.assertRaises(TypeError, nsw.__sub__, object())
        self.assertEqual(sorted(list(nsw)),
                         ['baz', 'norf', 'qux'])

    def test_str(self):
        self.assertEqual(self.sw.__str__(),
                         'Foo stop words: 3 words')

    def test_repr(self):
        self.assertEqual(self.sw.__repr__(),
                         "Foo stop words: ['bar', 'baz', 'foo']")


class StopWordRebaseTestCase(TestCase):

    def check_stop_word_rebase(self, inpout, outpout, sept, char=None):
        sw = StopWord('test', sept)
        if char is None:
            self.assertEqual(sw.rebase(inpout), outpout)
        else:
            self.assertEqual(sw.rebase(inpout, char), outpout)

    def test_stopword_rebase(self):
        """
        Basic rebasing
        """
        self.check_stop_word_rebase(
            'Comme je viens de te le dire',
            'XXXXX je viens de te le dire',
            ['comme'])
        self.check_stop_word_rebase(
            'Comme je viens de te le dire',
            'Comme je XXXXX de te le dire',
            ['viens'])
        self.check_stop_word_rebase(
            'Comme je viens de te le dire',
            'Comme je viens de te le XXXX',
            ['dire'])
        self.check_stop_word_rebase(
            'Comme je viens de te le dire',
            'Comme je viens de te le @@@@',
            ['dire'], '@')

    def test_stopword_rebase_newline(self):
        """
        Test with newline between two words
        """
        self.check_stop_word_rebase(
            'Comme je\nviens de te le dire',
            'Comme XX\nXXXXX de te le dire',
            ['viens', 'je'])
        self.check_stop_word_rebase(
            'Comme je\nviens de te le dire',
            'Comme XX\nviens de te le dire',
            ['je'])
        self.check_stop_word_rebase(
            'Comme je\nviens de te le dire',
            'Comme je\nXXXXX de te le dire',
            ['viens'])
        self.check_stop_word_rebase(
            'Comme je\n\tviens de te le dire',
            'Comme je\n\tXXXXX de te le dire',
            ['viens'])

    def test_stopword_dont_rebase(self):
        """
        Test with newline before word
        """
        self.check_stop_word_rebase(
            'Comme je viensbhgfds de te le dire',
            'Comme je viensbhgfds de te le dire',
            ['viens'])
        self.check_stop_word_rebase(
            'Comme je gfgviens de te le dire',
            'Comme je gfgviens de te le dire',
            ['viens'])
        self.check_stop_word_rebase(
            'Comme je gfgviensbhgfds de te le dire',
            'Comme je gfgviensbhgfds de te le dire',
            ['viens'])

    def test_stopword_empty(self):
        """
        Test with empty charactere to rebase
        """
        self.check_stop_word_rebase(
            'Comme je viens de te le dire',
            ' je viens de te le dire',
            ['comme'], '')
        self.check_stop_word_rebase(
            'Comme je viens de te le dire',
            'Comme je  de te le dire',
            ['viens'], '')
        self.check_stop_word_rebase(
            'Comme je\n\tviens de te le dire',
            'Comme je\n\t de te le dire',
            ['viens'], '')


class StopWordRebaseFunctionalTestCase(TestCase):
    maxDiff = None

    def test_stop_word_rebase_functional(self):
        current_dir = os.path.dirname(__file__)
        file_name = os.path.join(current_dir, 'corpus', 'french.txt')
        file_content = open(file_name, 'rb').read().decode('utf-8')
        solution_name = os.path.join(current_dir,
                                     'corpus', 'french_solution.txt')
        solution_content = open(solution_name, 'rb').read().decode('utf-8')

        factory = StopWordFactory()
        stop_words = factory.get_stop_words('fr')
        file_content_rebased = stop_words.rebase(file_content)
        self.assertEqual(file_content_rebased, solution_content)
