"""Urls for Zinnia random entries"""
from __future__ import absolute_import
from django.conf.urls import url

from zinnia.views.random import EntryRandom


urlpatterns = [
    url(r'^$',
        EntryRandom.as_view(),
        name='entry_random'),
]
