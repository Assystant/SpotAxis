from __future__ import absolute_import
from django.contrib import admin
from django.apps import apps

# Register your models here.

for model in  apps.get_app_config('customField').get_models():
    admin.site.register(model)