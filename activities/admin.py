from django.contrib import admin
from activities.models import *
from common.admin import CustomModelAdminAllFields

# Register your models here.
@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
	pass

admin.site.register(Notification)
