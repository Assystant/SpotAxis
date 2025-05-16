"""
URLs for Zinnia random entry view.

This endpoint redirects the user to a randomly selected published blog entry.

Useful for:
- "Surprise Me" buttons
- Random post widgets
- Discoverability features

View Used:
- EntryRandom: Selects and redirects to a random published Entry.
"""

from django.conf.urls import url
from zinnia.views.random import EntryRandom

urlpatterns = [
    # --------------------------------------------------------------
    # Random Entry View
    # Example: /random/
    # Redirects to a randomly selected published entry
    # Uses Entry.published.all().order_by('?')[0]
    # --------------------------------------------------------------
    url(r'^$',
        EntryRandom.as_view(),
        name='entry_random'),
]
