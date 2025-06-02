"""
Tests for shortcuts
"""
from unittest import TestCase

from mots_vides import stop_words
from mots_vides.stop_words import StopWord
from mots_vides.exceptions import StopWordError


class StopWordShortcutTestCase(TestCase):

    def test_stop_words(self):
        self.assertTrue(isinstance(stop_words('french'), StopWord))
        self.assertTrue(isinstance(stop_words('klingon'), StopWord))
        self.assertRaises(StopWordError, stop_words, 'klingon', False)
