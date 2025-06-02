"""Urls for the Zinnia tags"""
from __future__ import absolute_import
from django.urls import re_path

from zinnia.urls import _
from zinnia.views.tags import TagDetail
from zinnia.views.tags import TagList


urlpatterns = [
    re_path(r'^$',
        TagList.as_view(),
        name='tag_list'),
    re_path(r'^(?P<tag>[^/]+(?u))/$',
        TagDetail.as_view(),
        name='tag_detail'),
    re_path(_(r'^(?P<tag>[^/]+(?u))/page/(?P<page>\d+)/$'),
        TagDetail.as_view(),
        name='tag_detail_paginated'),
]
