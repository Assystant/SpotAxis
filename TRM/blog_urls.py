# -*- coding: utf-8 -*-

from __future__ import absolute_import
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.views.static import serve
from django.contrib.auth import views as django_auth_views
from common.forms import ChangePasswordForm, RecoverUserForm, CustomPasswordResetForm
from candidates import views as candidates_views
from common import views as common_views
from common import ajax as common_ajax_views
from companies import views as companies_views
from activities import views as activities_views
from TRM import views as TRM_views
from example import views as example_views
from payments import views as payments_views
from vacancies import views as vacancy_views
from socialmultishare import views as socialmultishare_views
from TRM import settings
from companies.views import upload_vacancy_file, delete_vacancy_file

admin.autodiscover()
handler500 = 'TRM.views.handler500'

# blog_urls = ([
#     path('', include('zinnia.urls.capabilities')),
#     path('search/', include('zinnia.urls.search')),
#     path('sitemap/', include('zinnia.urls.sitemap')),
#     path('trackback/', include('zinnia.urls.trackback')),
#     path('blog/tags/', include('zinnia.urls.tags')),
#     path('blog/feeds/', include('zinnia.urls.feeds')),
#     path('blog/random/', include('zinnia.urls.random')),
#     path('blog/authors/', include('zinnia.urls.authors')),
#     path('blog/categories/', include('zinnia.urls.categories')),
#     path('blog/comments/', include('zinnia.urls.comments')),
#     path('blog/', include('zinnia.urls.entries')),
#     path('blog/', include('zinnia.urls.archives')),
#     path('blog/', include('zinnia.urls.shortlink')),
#     path('blog/', include('zinnia.urls.quick_entry'))
# ], 'zinnia')

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', include('zinnia.urls')),
    path('comments/', include('django_comments.urls')),
    # path('', include(blog_urls))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#
# if settings.DEBUG:
urlpatterns += [
    path('media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]