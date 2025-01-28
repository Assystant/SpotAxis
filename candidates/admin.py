# # -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.conf import settings

from django.contrib import admin
from candidates.models import Candidate, Expertise, Academic_Area, Academic_Status, Academic, Language_Level, Language, CV_Language, Curriculum
from common.admin import CustomModelAdminAllFields


class CandidateAdmin(CustomModelAdminAllFields):
    list_filter = (('gender', admin.RelatedOnlyFieldListFilter),
                   'add_date')
    list_display_links = ('id', 'user')
    search_fields = ('id', 'user__username', 'user__first_name', 'user__last_name')
admin.site.register(Candidate, CandidateAdmin)


class ExpertiseAdmin(CustomModelAdminAllFields):
    list_filter = (('industry', admin.RelatedOnlyFieldListFilter),)
    list_display_links = ('candidate',)
    search_fields = ('id', 'candidate__id', 'candidate__user__username', 'candidate__user__first_name')
admin.site.register(Expertise, ExpertiseAdmin)


class AcademicAreaAdmin(CustomModelAdminAllFields):
    pass
admin.site.register(Academic_Area, AcademicAreaAdmin)


class AcademicStatusAdmin(CustomModelAdminAllFields):
    pass
admin.site.register(Academic_Status, AcademicStatusAdmin)


class AcademicAdmin(CustomModelAdminAllFields):
    list_filter = (('degree', admin.RelatedOnlyFieldListFilter),
                   ('status', admin.RelatedOnlyFieldListFilter))
    list_display_links = ('id', 'candidate')
    search_fields = ('id', 'candidate__first_name', 'candidate__last_name', 'school')
admin.site.register(Academic, AcademicAdmin)


class LanguageAdmin(CustomModelAdminAllFields):
    pass
admin.site.register(Language, LanguageAdmin)


class CVLanguageAdmin(CustomModelAdminAllFields):
    list_filter = (('language', admin.RelatedOnlyFieldListFilter),)
    list_display_links = ('id', 'candidate')
admin.site.register(CV_Language, CVLanguageAdmin)

class CurriculumAdmin(CustomModelAdminAllFields):
    list_filter = ('last_modified', 'add_date')
    list_display_links = ('id', 'candidate')
    search_fields = ('id', 'candidate__first_name')
admin.site.register(Curriculum, CurriculumAdmin)
