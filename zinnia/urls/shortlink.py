"""Urls for the Zinnia entries short link"""
from __future__ import absolute_import
from django.conf.urls import url

from zinnia.views.shortlink import EntryShortLink


urlpatterns = [
    url(r'^(?P<token>[\dA-Z]+)/$',
        EntryShortLink.as_view(),
        name='entry_shortlink'),
]
