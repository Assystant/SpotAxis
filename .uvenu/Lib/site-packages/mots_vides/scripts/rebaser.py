"""
Rebaser command line script for printing text file with stop words rebased
"""
import sys
from argparse import ArgumentParser


from mots_vides.factory import StopWordFactory


def cmdline(argv=sys.argv[1:]):
    """
    Script for rebasing a text file
    """
    parser = ArgumentParser(
        description='Rebase a text from his stop words')
    parser.add_argument('language', help='The language used to rebase')
    parser.add_argument('source', help='Text file to rebase')
    options = parser.parse_args(argv)

    factory = StopWordFactory()
    language = options.language
    stop_words = factory.get_stop_words(language, fail_safe=True)
    content = open(options.source, 'rb').read().decode('utf-8')
    print(stop_words.rebase(content))
