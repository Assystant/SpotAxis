"""
Admin module for dynamically registering all models from the 'customField' app.

This script automatically retrieves all models defined in the 'customField' app and registers
them with the Django admin site, making them available in the Django admin interface without
manually registering each model individually.
"""
from __future__ import absolute_import
from django.contrib import admin
from django.apps import apps

# Register your models here.

for model in  apps.get_app_config('customField').get_models():
    admin.site.register(model)