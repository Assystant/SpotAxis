"""Defaults urls for the Zinnia project"""
from __future__ import absolute_import
from django.conf.urls import include
from django.conf.urls import url
from django.utils.translation import gettext_lazy as _

from zinnia.settings import TRANSLATED_URLS


def i18n_url(url, translate=TRANSLATED_URLS):
    """
    Translate or not an URL part.
    """
    if translate:
        return gettext_lazy(url)
    return url

_ = i18n_url

app_name = 'zinnia'

urlpatterns = [
    url(_(r'^feeds/'), include('zinnia.urls.feeds')),
    url(_(r'^tags/'), include('zinnia.urls.tags')),
    url(_(r'^authors/'), include('zinnia.urls.authors')),
    url(_(r'^search/'), include('zinnia.urls.search')),
    url(_(r'^random/'), include('zinnia.urls.random')),
    url(_(r'^sitemap/'), include('zinnia.urls.sitemap')),
    url(_(r'^trackback/'), include('zinnia.urls.trackback')),
    url(_(r'^comments/'), include('zinnia.urls.comments')),
    url(_(r'^s/'), include('zinnia.urls.shortlink')),
    url(r'^', include('zinnia.urls.entries')),
    url(r'^', include('zinnia.urls.archives')),
    url(r'^', include('zinnia.urls.quick_entry')),
    url(r'^', include('zinnia.urls.capabilities')),
    url(r'^', include('zinnia.urls.categories')),
]
