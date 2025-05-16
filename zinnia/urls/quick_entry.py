"""
URL for the Zinnia quick entry view.

This endpoint allows staff users to quickly publish or draft a blog entry
through a simplified form, bypassing the full admin interface.

View Used:
- QuickEntry: Handles GET (redirect to admin) and POST (quick-create entry)

Intended for power users or API-style clients who need a faster publishing workflow.
"""

from django.conf.urls import url

from zinnia.urls import _  # Optional i18n support for translated URLs
from zinnia.views.quick_entry import QuickEntry

urlpatterns = [
    # --------------------------------------------------------------
    # Quick Entry Post View
    # Example: /quick-entry/
    # GET -> redirects to admin entry creation form
    # POST -> creates and publishes or drafts a new blog entry
    # Requires `zinnia.add_entry` permission
    # --------------------------------------------------------------
    url(_(r'^quick-entry/$'),
        QuickEntry.as_view(),
        name='entry_quick_post'),
]
