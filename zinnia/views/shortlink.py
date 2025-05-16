"""
Views for Zinnia shortlink support.

This module defines a redirect view that resolves a base36-encoded 
shortlink token to a blog entry's full URL.
"""

from django.shortcuts import get_object_or_404
from django.views.generic.base import RedirectView

from zinnia.models.entry import Entry


class EntryShortLink(RedirectView):
    """
    Redirect view that resolves a shortlink to the full entry URL.

    This enables support for URLs like:
        /e/abc123/
    where 'abc123' is a base36-encoded primary key (ID) of a blog entry.

    Attributes:
        permanent (bool): Whether the redirect should be HTTP 301 (True) or 302 (False).
    """
    permanent = True  # Use HTTP 301 Moved Permanently

    def get_redirect_url(self, **kwargs):
        """
        Decode the base36-encoded primary key ('token') and retrieve the entry.

        Args:
            token (str): A base36-encoded string representing the entry's primary key.

        Returns:
            str: The absolute URL of the matching Entry object.

        Raises:
            Http404: If no matching published Entry is found.
        """
        # Convert base36 string to integer PK
        entry_id = int(kwargs['token'], 36)

        # Fetch the entry or raise 404
        entry = get_object_or_404(Entry.published, pk=entry_id)

        # Redirect to the entry's full canonical URL
        return entry.get_absolute_url()
