from __future__ import absolute_import
from django.urls import path
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache
from .views import UploadImageAPIView, BrowseImagesAPIView


urlpatterns = [
    path('upload/', staff_member_required(UploadImageAPIView), name='ckeditor_upload'),
    path('browse/', never_cache(staff_member_required(BrowseImagesAPIView)), name='ckeditor_browse'),
]
