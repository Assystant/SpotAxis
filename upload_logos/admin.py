# -*- coding: utf-8 -*-
from django.contrib import admin
from upload_logos.models import UploadedFile


class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('file','creation_date')
    date_hierarchy = 'creation_date'
    search_fields = ('file',)
admin.site.register(UploadedFile, UploadedFileAdmin)
