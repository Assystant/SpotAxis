from __future__ import absolute_import
from django.urls import path
from upload_logos.views import upload

urlpatterns = [
    path('', upload, name='ajax-upload'),
]
