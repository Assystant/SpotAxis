"""
Tests for StopWordFactory
"""
import os
from tempfile import NamedTemporaryFile

from unittest import TestCase

from mots_vides.stop_words import StopWord
from mots_vides.factory import StopWordFactory
from mots_vides.exceptions import StopWordError


class StopWordFactoryTestCase(TestCase):

    def setUp(self):
        self.data_directory = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)),
            'datas/')
        self.factory = StopWordFactory(self.data_directory,
                                       {'kl': 'klingon',
                                        'si': 'sindarin'})

    def test_get_stopwords(self):
        sw = self.factory.get_stop_words('klingon')
        self.assertTrue(isinstance(sw, StopWord))
        self.assertEqual(sorted(list(sw.collection)),
                         ["HIja'", "ghobe'", 'naDev', 'nuq'])

    def test_get_stopwords_shortcuts(self):
        sw = self.factory.get_stop_words('kl')
        self.assertEqual(sorted(list(sw.collection)),
                         ["HIja'", "ghobe'", 'naDev', 'nuq'])

    def test_get_stopwords_unavailable_language(self):
        self.assertRaises(StopWordError, self.factory.get_stop_words, 'vulcan')
        sw = self.factory.get_stop_words('vulcan', fail_safe=True)
        self.assertEqual(list(sw.collection), [])

    def test_get_stopwords_file_unreadable(self):
        self.factory.available_languages  # Fill the cache, pass security
        self.factory.data_directory = '/brutal/change/'
        self.assertRaises(StopWordError,
                          self.factory.get_stop_words, 'klingon')
        sw = self.factory.get_stop_words('klingon', fail_safe=True)
        self.assertEqual(list(sw.collection), [])

    def test_get_stopwords_cache(self):
        self.assertEqual(self.factory.LOADED_LANGUAGES_CACHE, {})
        self.factory.get_stop_words('klingon')
        self.assertEqual(list(self.factory.LOADED_LANGUAGES_CACHE.keys()),
                         ['klingon'])
        sw = self.factory.get_stop_words('kl')
        self.assertEqual(list(self.factory.LOADED_LANGUAGES_CACHE.keys()),
                         ['klingon'])
        self.factory.data_directory = '/brutal/change/'
        self.assertEqual(sw.collection,
                         self.factory.get_stop_words('klingon').collection)

    def test_get_stopwords_cache_and_errors(self):
        self.assertRaises(StopWordError, self.factory.get_stop_words, 'vulcan')
        self.assertRaises(StopWordError, self.factory.get_stop_words, 'vulcan')
        self.assertEqual(self.factory.LOADED_LANGUAGES_CACHE, {})
        self.factory.get_stop_words('vulcan', fail_safe=True)
        self.assertEqual(self.factory.LOADED_LANGUAGES_CACHE, {})
        self.assertRaises(StopWordError, self.factory.get_stop_words, 'vulcan')

    def test_get_stopwords_cache_twice_python3(self):
        sw = self.factory.get_stop_words('klingon')
        self.assertEquals(len(sw), len(self.factory.get_stop_words('klingon')))

    def test_available_languages(self):
        self.assertEqual(self.factory.available_languages,
                         ['klingon', 'sindarin'])
        self.factory.data_directory = '/brutal/change/'
        self.assertEqual(self.factory.available_languages,
                         ['klingon', 'sindarin'])

    def test_available_languages_error(self):
        self.factory.data_directory = '/brutal/change/'
        self.assertRaises(StopWordError,
                          lambda: self.factory.available_languages)

    def test_get_collection_filename(self):
        filename = self.factory.get_collection_filename('foo')
        self.assertTrue(filename.endswith('foo.txt'))
        self.assertTrue(filename.startswith(self.data_directory))

    def test_read_collection(self):
        collection_file = NamedTemporaryFile()
        collection_text = 'egor\n\n   \nai\n'
        collection_file.write(collection_text.encode('utf-8'))
        collection_file.seek(0)
        collection = self.factory.read_collection(collection_file.name)
        self.assertEqual(list(collection), ['egor', 'ai'])
        collection_file.close()

    def test_write_collection(self):
        collection_file = NamedTemporaryFile()
        self.factory.write_collection(
            collection_file.name,
            ['nuq', "HIja'", "ghobe'", 'naDev'])
        collection_file.seek(0)
        self.assertEqual(collection_file.read().decode('utf-8'),
                         "HIja'\nghobe'\nnaDev\nnuq")
        collection_file.close()
