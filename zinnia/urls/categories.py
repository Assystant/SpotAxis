"""Urls for the Zinnia categories"""
from __future__ import absolute_import
from django.conf.urls import url

from zinnia.urls import _
from zinnia.views.categories import CategoryDetail
from zinnia.views.categories import CategoryList


urlpatterns = [
    url(r'^category/$',
        CategoryList.as_view(),
        name='category_list'),
    url(_(r'^(?P<path>[-\/\w]+)/page/(?P<page>\d+)/$'),
        CategoryDetail.as_view(),
        name='category_detail_paginated'),
    url(r'^(?P<path>[-\/\w]+)/$',
        CategoryDetail.as_view(),
        name='category_detail'),
]
