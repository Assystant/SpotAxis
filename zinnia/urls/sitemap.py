"""Urls for the Zinnia sitemap"""
from __future__ import absolute_import
from django.conf.urls import url

from zinnia.views.sitemap import Sitemap


urlpatterns = [
    url(r'^$', Sitemap.as_view(),
        name='sitemap'),
]
