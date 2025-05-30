"""Test urls for tagging."""
from django.conf.urls import url

from tagging.tests.models import Article
from tagging.views import TaggedObjectList


class StaticTaggedObjectList(TaggedObjectList):
    tag = 'static'
    queryset = Article.objects.all()


urlpatterns = [
    url(r'^static/$', StaticTaggedObjectList.as_view()),
    url(r'^static/related/$', StaticTaggedObjectList.as_view(
        related_tags=True)),
    url(r'^no-tag/$', TaggedObjectList.as_view(model=Article)),
    url(r'^no-query-no-model/$', TaggedObjectList.as_view()),
    url(r'^(?P<tag>[^/]+(?u))/$', TaggedObjectList.as_view(model=Article)),
]
