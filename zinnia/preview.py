"""
Preview for Zinnia

This module defines the `HTMLPreview` class used to build smart previews of HTML content
for blog entries in the Zinnia CMS.

It supports:
- Splitting at predefined markers (e.g., <!--more-->)
- Truncating to a max word limit while preserving HTML structure
- Counting total, displayed, and remaining words
- Calculating display/remaining content percentage
"""

from __future__ import division

from bs4 import BeautifulSoup
from django.utils import six
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.html import strip_tags
from django.utils.text import Truncator

from zinnia.settings import (
    PREVIEW_MAX_WORDS,
    PREVIEW_MORE_STRING,
    PREVIEW_SPLITTERS
)


@python_2_unicode_compatible
class HTMLPreview(object):
    """
    Generate an HTML-safe preview of a longer HTML content block.

    Preview logic is based on:
    - Using a `lead` if provided (prioritized)
    - Looking for predefined "splitters" like `<!--more-->`
    - Truncating to a max word count with a trailing string like "... more"

    Attributes:
        content (str): Full HTML content.
        lead (str): Optional lead/intro text to show before content.
        splitters (list): Markers that define explicit cut-off points in content.
        max_words (int): Maximum number of words if no splitter is found.
        more_string (str): Trailing string to append when preview is truncated.
    """

    def __init__(self, content, lead='',
                 splitters=PREVIEW_SPLITTERS,
                 max_words=PREVIEW_MAX_WORDS,
                 more_string=PREVIEW_MORE_STRING):
        self._preview = None
        self.lead = lead
        self.content = content
        self.splitters = splitters
        self.max_words = max_words
        self.more_string = more_string

    @property
    def preview(self):
        """
        Return the preview content (built once and cached).

        Returns:
            str or BeautifulSoup object: The HTML preview content.
        """
        if self._preview is None:
            self._preview = self.build_preview()
        return self._preview

    @property
    def has_more(self):
        """
        Whether the preview is a shortened version of the content.

        Returns:
            bool: True if preview != full content.
        """
        return bool(self.content and self.preview != self.content)

    def __str__(self):
        """
        Return string representation for rendering in templates.

        Returns:
            str: HTML-safe preview as string.
        """
        return six.text_type(self.preview)

    def build_preview(self):
        """
        Core logic for building the preview.

        Follows this order:
        1. Use lead if provided
        2. Use content up to a splitter (like <!--more-->)
        3. Truncate to a fixed word limit
        """
        if self.lead:
            return self.lead
        for splitter in self.splitters:
            if splitter in self.content:
                return self.split(splitter)
        return self.truncate()

    def truncate(self):
        """
        Truncate the HTML content by word count using Django's Truncator.

        Returns:
            str: Truncated HTML-safe string with `more_string` appended.
        """
        return Truncator(self.content).words(
            self.max_words, self.more_string, html=True)

    def split(self, splitter):
        """
        Split HTML content by a marker (e.g., <!--more-->) while preserving valid HTML.

        Returns:
            BeautifulSoup: Parsed and trimmed HTML with more_string appended.
        """
        soup = BeautifulSoup(self.content.split(splitter)[0], 'html.parser')
        last_string = soup.find_all(text=True)[-1]
        last_string.replace_with(last_string.string + self.more_string)
        return soup

    @cached_property
    def total_words(self):
        """
        Count total words in the combined lead and content (raw, not HTML-safe).

        Returns:
            int: Total word count.
        """
        return len(strip_tags(f'{self.lead} {self.content}').split())

    @cached_property
    def displayed_words(self):
        """
        Count the number of words actually shown in the preview.

        Returns:
            int: Word count shown.
        """
        return len(strip_tags(self.preview).split()) - (
            len(self.more_string.split()) * int(not bool(self.lead))
        )

    @cached_property
    def remaining_words(self):
        """
        Count number of words hidden after the preview.

        Returns:
            int: Remaining (hidden) word count.
        """
        return self.total_words - self.displayed_words

    @cached_property
    def displayed_percent(self):
        """
        Calculate percentage of content shown.

        Returns:
            float: Percentage displayed.
        """
        return (self.displayed_words / self.total_words) * 100

    @cached_property
    def remaining_percent(self):
        """
        Calculate percentage of content hidden.

        Returns:
            float: Percentage not shown.
        """
        return (self.remaining_words / self.total_words) * 100
