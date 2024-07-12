"""Test urls for the zinnia project"""
from django.conf.urls import url

from zinnia.tests.implementations.urls.default import (
    urlpatterns as test_urlpatterns)
from zinnia.views.authors import AuthorDetail
from zinnia.views.categories import CategoryDetail
from zinnia.views.tags import TagDetail


class CustomModelDetailMixin(object):
    """
    Mixin for changing the template_name
    and overriding the context.
    """
    template_name = 'zinnia/entry_custom_list.html'

    def get_context_data(self, **kwargs):
        context = super(CustomModelDetailMixin,
                        self).get_context_data(**kwargs)
        context.update({'extra': 'context'})
        return context


class CustomTagDetail(CustomModelDetailMixin, TagDetail):
    pass


class CustomAuthorDetail(CustomModelDetailMixin, AuthorDetail):
    pass


class CustomCategoryDetail(CustomModelDetailMixin, CategoryDetail):
    pass


urlpatterns = [
    url(r'^authors/(?P<username>[.+-@\w]+)/$',
        CustomAuthorDetail.as_view(),
        name='zinnia_author_detail'),
    url(r'^authors/(?P<username>[.+-@\w]+)/page/(?P<page>\d+)/$',
        CustomAuthorDetail.as_view(),
        name='zinnia_author_detail_paginated'),
    url(r'^categories/(?P<path>[-\/\w]+)/page/(?P<page>\d+)/$',
        CustomCategoryDetail.as_view(),
        name='zinnia_category_detail_paginated'),
    url(r'^categories/(?P<path>[-\/\w]+)/$',
        CustomCategoryDetail.as_view(),
        name='zinnia_category_detail'),
    url(r'^tags/(?P<tag>[^/]+(?u))/$',
        CustomTagDetail.as_view(),
        name='zinnia_tag_detail'),
    url(r'^tags/(?P<tag>[^/]+(?u))/page/(?P<page>\d+)/$',
        CustomTagDetail.as_view(),
        name='zinnia_tag_detail_paginated'),
] + test_urlpatterns
