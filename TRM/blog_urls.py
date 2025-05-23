# -*- coding: utf-8 -*-

from __future__ import absolute_import
from django.conf.urls import *
# from django.conf import settings
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
# from django.views.generic.simple import direct_to_template
from companies.views import upload_vacancy_file, delete_vacancy_file

admin.autodiscover()
handler500 = 'TRM.views.handler500'

# blog_urls = ([
#     url(r'^', include('zinnia.urls.capabilities')),
#     url(r'^search/', include('zinnia.urls.search')),
#     url(r'^sitemap/', include('zinnia.urls.sitemap')),
#     url(r'^trackback/', include('zinnia.urls.trackback')),
#     url(r'^blog/tags/', include('zinnia.urls.tags')),
#     url(r'^blog/feeds/', include('zinnia.urls.feeds')),
#     url(r'^blog/random/', include('zinnia.urls.random')),
#     url(r'^blog/authors/', include('zinnia.urls.authors')),
#     url(r'^blog/categories/', include('zinnia.urls.categories')),
#     url(r'^blog/comments/', include('zinnia.urls.comments')),
#     url(r'^blog/', include('zinnia.urls.entries')),
#     url(r'^blog/', include('zinnia.urls.archives')),
#     url(r'^blog/', include('zinnia.urls.shortlink')),
#     url(r'^blog/', include('zinnia.urls.quick_entry'))
# ], 'zinnia')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('zinnia.urls')),
	url(r'^comments/', include('django_comments.urls')),


	# url(r'^', include(blog_urls))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#
# if settings.DEBUG:
urlpatterns += [
    url(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]