"""
Factory for getting initialized StopWord collections.
"""
import os

from mots_vides.stop_words import StopWord
from mots_vides.exceptions import StopWordError
from mots_vides.constants import DATA_DIRECTORY
from mots_vides.constants import LANGUAGE_CODES


class StopWordFactory(object):
    """
    Factory managing the collections of stop words by languages.
    """

    def __init__(self, data_directory=DATA_DIRECTORY,
                 language_codes=LANGUAGE_CODES):
        """
        Initializes the factory with the directory path where to find
        the collections of stop words.
        """
        self.data_directory = data_directory
        self.language_codes = language_codes
        self.LOADED_LANGUAGES_CACHE = {}

    def get_stop_words(self, language, fail_safe=False):
        """
        Returns a StopWord object initialized with the stop words collection
        requested by ``language``.
        If the requested language is not available a StopWordError is raised.
        If ``fail_safe`` is set to True, an empty StopWord object is returned.
        """
        try:
            language = self.language_codes[language]
        except KeyError:
            pass

        collection = self.LOADED_LANGUAGES_CACHE.get(language)

        if collection is None:
            try:
                collection = self._get_stop_words(language)
                self.LOADED_LANGUAGES_CACHE[language] = collection
            except StopWordError as error:
                if not fail_safe:
                    raise error
                collection = []

        stop_words = StopWord(language, collection)
        return stop_words

    def _get_stop_words(self, language):
        """
        Internal method for getting the stop words collections
        and raising errors.
        """
        if language not in self.available_languages:
            raise StopWordError(
                'Stop words are not available in "%s".\n'
                'If possible do a pull request at : '
                'https://github.com/Fantomas42/mots-vides' %
                language)
        try:
            filename = self.get_collection_filename(language)
            collection = self.read_collection(filename)
        except IOError:
            raise StopWordError(
                '"%s" file is unreadable, check your installation.' %
                filename)
        return collection

    @property
    def available_languages(self):
        """
        Returns a list of languages providing collection of stop words.
        """
        available_languages = getattr(self, '_available_languages', None)
        if available_languages:
            return available_languages
        try:
            languages = os.listdir(self.data_directory)
        except OSError:
            raise StopWordError(
                "'datas' directory is unreadable, check your installation.")
        languages = sorted(map(lambda x: x.replace('.txt', ''), languages))
        setattr(self, '_available_languages', languages)
        return languages

    """
    Here the tools for the (de)serialization of the collection files.
    """

    def get_collection_filename(self, language):
        """
        Returns the filename containing the stop words collection
        for a specific language.
        """
        filename = os.path.join(self.data_directory, '%s.txt' % language)
        return filename

    def read_collection(self, filename):
        """
        Reads and returns a collection of stop words into a file.
        """
        with open(filename, 'rb') as fd:
            lines = fd.read().decode('utf-8-sig').splitlines()
        collection = list(filter(bool, [line.strip() for line in lines]))
        return collection

    def write_collection(self, filename, collection):
        """
        Writes a collection of stop words into a file.
        """
        collection = sorted(list(collection))
        with open(filename, 'wb+') as fd:
            fd.truncate()
            fd.write('\n'.join(collection).encode('utf-8'))
