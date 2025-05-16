"""
URLs for the Zinnia trackback endpoint.

Trackbacks allow external blogs to notify your blog when they link to one of your entries.

This endpoint:
- Accepts trackbacks via `POST`
- Redirects to the entry page on `GET`
- Responds with an XML confirmation or error message

View Used:
- EntryTrackback: Handles trackback submission and validation.
"""

from django.conf.urls import url
from zinnia.views.trackback import EntryTrackback

urlpatterns = [
    # ------------------------------------------------------------------
    # Trackback Endpoint for an Entry
    # Example: /trackback/123/
    # Handles:
    # - GET: redirects to the full blog entry
    # - POST: registers a trackback for entry with ID 123
    # ------------------------------------------------------------------
    url(r'^(?P<pk>\d+)/$',
        EntryTrackback.as_view(),
        name='entry_trackback'),
]
