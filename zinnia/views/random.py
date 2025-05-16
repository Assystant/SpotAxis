"""
View for displaying a random blog entry.

This module defines a redirect view that sends the user
to a randomly selected published entry.
"""

from django.views.generic.base import RedirectView
from zinnia.models.entry import Entry


class EntryRandom(RedirectView):
    """
    Redirect view that takes the user to a random published Entry.

    Useful for features like "Surprise Me", "Random Post", or
    keeping users engaged with old but relevant content.

    Attributes:
        permanent (bool): Whether the redirect should be permanent (301) or temporary (302).
    """
    permanent = False  # Use 302 Temporary Redirect

    def get_redirect_url(self, **kwargs):
        """
        Select a random published entry and redirect to its absolute URL.

        Returns:
            str: URL of the randomly chosen entry.
        """
        entry = Entry.published.all().order_by('?')[0]
        return entry.get_absolute_url()
