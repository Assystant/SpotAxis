from __future__ import absolute_import
from django.contrib import admin
from scheduler.models import *
from common.admin import CustomModelAdminAllFields

"""
Admin configuration for the scheduler app.

Registers the Schedule model with the Django admin site and customizes
its admin interface for better usability.

Imports:
    - admin: Django admin site framework.
    - Schedule: The Schedule model from the scheduler app.
    - CustomModelAdminAllFields: Custom admin base class with all fields enabled.
"""

# Register your models here.

class ScheduleAdmin(CustomModelAdminAllFields):
    """
    Admin interface customization for the Schedule model.

    Features:
        - Filters schedules by their status.
        - Displays key fields in the schedule list view.
        - Enables clickable links on ID and scheduled date.
        - Allows searching schedules by user and candidate names and email.
    """
    list_filter = ('status',)
    list_display = ('id', 'scheduled_on', 'offset', 'user', 'application__candidate', 'status')
    list_display_links = ('id', 'scheduled_on')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'application__candidate__first_name', 'application__candidate__last_name', 'get_status_display')
admin.site.register(Schedule, ScheduleAdmin)
