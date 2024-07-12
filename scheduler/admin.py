from django.contrib import admin
from scheduler.models import *
from common.admin import CustomModelAdminAllFields

# Register your models here.

class ScheduleAdmin(CustomModelAdminAllFields):
    list_filter = ('status',)
    list_display = ('id', 'scheduled_on', 'offset', 'user', 'application__candidate', 'status')
    list_display_links = ('id', 'scheduled_on')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'application__candidate__first_name', 'application__candidate__last_name', 'get_status_display')
admin.site.register(Schedule, ScheduleAdmin)
