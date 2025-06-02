"""
Merger command line script for building collections of stop words
"""
import sys
from argparse import ArgumentParser

from mots_vides.stop_words import StopWord
from mots_vides.factory import StopWordFactory


def cmdline(argv=sys.argv[1:]):
    """
    Script for merging different collections of stop words.
    """
    parser = ArgumentParser(
        description='Create and merge collections of stop words')
    parser.add_argument(
        'language', help='The language used in the collection')
    parser.add_argument('sources', metavar='FILE', nargs='+',
                        help='Source files to parse')
    options = parser.parse_args(argv)

    factory = StopWordFactory()
    language = options.language
    stop_words = factory.get_stop_words(language, fail_safe=True)

    for filename in options.sources:
        stop_words += StopWord(language, factory.read_collection(filename))

    filename = factory.get_collection_filename(stop_words.language)
    factory.write_collection(filename, stop_words.collection)
