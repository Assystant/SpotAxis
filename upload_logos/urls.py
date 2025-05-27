from __future__ import absolute_import
from django.urls import re_path
from upload_logos.views import upload

urlpatterns = [
    re_path(r'^$', upload, name='ajax-upload'),
]
