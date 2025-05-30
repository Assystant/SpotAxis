"""Urls for Zinnia random entries"""
from __future__ import absolute_import
from django.urls import re_path

from zinnia.views.random import EntryRandom


urlpatterns = [
    re_path(r'^$',
        EntryRandom.as_view(),
        name='entry_random'),
]
