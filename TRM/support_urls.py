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

urlpatterns = [
    # url(r'helpdesk/', include('helpdesk.urls')),
    # url(r'', include('helpdesk.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#
# if settings.DEBUG:
urlpatterns += [
    path('media/<path:path>', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]