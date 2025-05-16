"""
Views for Zinnia entries.

This module provides detail views for individual blog entries,
with support for:
- Date-based URL resolution
- Entry preview handling
- Password protection
- Caching
"""

from django.views.generic.dates import BaseDateDetailView

from zinnia.models.entry import Entry
from zinnia.views.mixins.archives import ArchiveMixin
from zinnia.views.mixins.callable_queryset import CallableQuerysetMixin
from zinnia.views.mixins.entry_cache import EntryCacheMixin
from zinnia.views.mixins.entry_preview import EntryPreviewMixin
from zinnia.views.mixins.entry_protection import EntryProtectionMixin
from zinnia.views.mixins.templates import EntryArchiveTemplateResponseMixin


class EntryDateDetail(ArchiveMixin,
                      EntryArchiveTemplateResponseMixin,
                      CallableQuerysetMixin,
                      BaseDateDetailView):
    """
    View for retrieving a single Entry based on its publication date and slug.

    Combines the following mixins:
    - `ArchiveMixin`: Provides shared configuration (like date field, formats).
    - `EntryArchiveTemplateResponseMixin`: Selects custom templates for entries.
    - `CallableQuerysetMixin`: Defers queryset execution until runtime.
    - `BaseDateDetailView`: Core Django CBV to retrieve object by date and slug.

    Queryset is scoped to:
    - Published entries
    - Entries associated with the current site (via `on_site` manager)
    """
    queryset = Entry.published.on_site


class EntryDetail(EntryCacheMixin,
                  EntryPreviewMixin,
                  EntryProtectionMixin,
                  EntryDateDetail):
    """
    Full-featured detail view for a single Entry.

    Adds:
    - `EntryCacheMixin`: Enables per-entry caching for performance.
    - `EntryPreviewMixin`: Allows previewing unpublished or future entries.
    - `EntryProtectionMixin`: Handles login and password protection for entries.

    Inherits date-based URL resolution and template handling from `EntryDateDetail`.
    """
