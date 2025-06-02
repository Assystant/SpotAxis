"""Urls for the Zinnia sitemap"""
from __future__ import absolute_import
from django.urls import re_path

from zinnia.views.sitemap import Sitemap


urlpatterns = [
    re_path(r'^$', Sitemap.as_view(),
        name='sitemap'),
]
