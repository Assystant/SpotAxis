from __future__ import absolute_import
from django.urls import path
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache

from ckeditor import views

"""
URL configuration module for CKEditor integration in a Django project.

Defines URL patterns for handling CKEditor image upload and browsing views.
Access to these views is restricted to staff members, with caching disabled
for the browsing view to ensure fresh content.
"""
urlpatterns = [
    path('upload/', staff_member_required(views.upload), name='ckeditor_upload'),
    path('browse/', never_cache(staff_member_required(views.browse)), name='ckeditor_browse'),
]
