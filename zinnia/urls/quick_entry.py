"""Url for the Zinnia quick entry view"""
from __future__ import absolute_import
from django.urls import re_path

from zinnia.urls import _
from zinnia.views.quick_entry import QuickEntry


urlpatterns = [
    re_path(_(r'^quick-entry/$'),
        QuickEntry.as_view(),
        name='entry_quick_post'),
]
