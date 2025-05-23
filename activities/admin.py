"""
Admin interface configuration for the activities application.

This module registers the Activity and Notification models with the Django admin interface,
providing a user-friendly way to manage activities and notifications through the admin panel.
It uses custom admin classes to enhance the admin interface functionality.
"""

from __future__ import absolute_import
from django.contrib import admin
from activities.models import *
from common.admin import CustomModelAdminAllFields

# Register your models here.
@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
	"""Admin interface configuration for the Activity model.
	
	This class customizes how Activity objects are displayed and managed in the Django admin interface.
	Currently uses default ModelAdmin settings, but can be extended with custom list displays,
	filters, and search fields as needed.
	"""
	pass

admin.site.register(Notification)
