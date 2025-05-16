"""
Set of "markup" functions to transform plain text into HTML for Zinnia.

Originally adapted from `django.contrib.markup`.

This module supports multiple markup languages including:
- Markdown
- Textile
- reStructuredText

The markup used depends on the `MARKUP_LANGUAGE` setting in Zinnia.
"""

import warnings

from django.utils.encoding import force_bytes, force_text
from django.utils.html import linebreaks

from zinnia.settings import (
    MARKDOWN_EXTENSIONS,
    MARKUP_LANGUAGE,
    RESTRUCTUREDTEXT_SETTINGS
)


def textile(value):
    """
    Convert plain text written in Textile markup to HTML.

    Requires the `textile` Python library.

    Args:
        value (str): The Textile-formatted text.

    Returns:
        str: HTML output or original input if textile is not available.
    """
    try:
        import textile
    except ImportError:
        warnings.warn("The Python textile library isn't installed.",
                      RuntimeWarning)
        return value

    return textile.textile(force_text(value),
                           encoding='utf-8', output='utf-8')


def markdown(value, extensions=MARKDOWN_EXTENSIONS):
    """
    Convert Markdown text to HTML using the `markdown` library.

    Args:
        value (str): Markdown-formatted text.
        extensions (list): List of Markdown extensions to use.

    Returns:
        str: HTML output or original input if markdown is not available.
    """
    try:
        import markdown
    except ImportError:
        warnings.warn("The Python markdown library isn't installed.",
                      RuntimeWarning)
        return value

    return markdown.markdown(force_text(value), extensions=extensions)


def restructuredtext(value, settings=RESTRUCTUREDTEXT_SETTINGS):
    """
    Convert reStructuredText to HTML using `docutils`.

    Args:
        value (str): reStructuredText-formatted text.
        settings (dict): Optional docutils settings.

    Returns:
        str: HTML fragment or original input if docutils is not available.
    """
    try:
        from docutils.core import publish_parts
    except ImportError:
        warnings.warn("The Python docutils library isn't installed.",
                      RuntimeWarning)
        return value

    parts = publish_parts(source=force_bytes(value),
                          writer_name='html4css1',
                          settings_overrides=settings)
    return force_text(parts['fragment'])


def html_format(value):
    """
    Convert plain text to HTML using the configured MARKUP_LANGUAGE.

    If no markup language is configured, falls back to Django's linebreaks
    unless the value already contains paragraph tags.

    Args:
        value (str): The raw input string.

    Returns:
        str: HTML-formatted output.
    """
    if not value:
        return ''
    elif MARKUP_LANGUAGE == 'markdown':
        return markdown(value)
    elif MARKUP_LANGUAGE == 'textile':
        return textile(value)
    elif MARKUP_LANGUAGE == 'restructuredtext':
        return restructuredtext(value)
    elif '</p>' not in value:
        return linebreaks(value)
    return value
