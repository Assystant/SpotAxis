"""Test cases for zinnia.models_bases"""
from __future__ import absolute_import
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from zinnia.models_bases import load_model_class
from zinnia.models_bases.entry import AbstractEntry


class LoadModelClassTestCase(TestCase):
    """Tests dynamic model class importing via load_model_class."""
    def test_load_model_class(self):
        self.assertEqual(
            load_model_class('zinnia.models_bases.entry.AbstractEntry'),
            AbstractEntry)
        self.assertRaises(ImproperlyConfigured,
                          load_model_class, 'invalid.path.models.Toto')
