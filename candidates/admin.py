
"""
Admin configuration for the `candidates` app.

This module registers models related to candidates (such as Candidate, Expertise, Academic,
Language, and Curriculum) with Django's admin interface, allowing administrators to view
and manage candidate-related data.

It extends a custom admin base class `CustomModelAdminAllFields` from `common.admin` for 
a consistent admin layout across all models. Custom filters, search fields, and display
options are applied to improve usability.
"""

# # -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.conf import settings
from django.contrib import admin
from candidates.models import Candidate, Expertise, Academic_Area, Academic_Status, Academic, Language_Level, Language, CV_Language, Curriculum
from common.admin import CustomModelAdminAllFields


class CandidateAdmin(CustomModelAdminAllFields):
    """
    Admin interface for the `Candidate` model.

    Adds filters for gender and add_date, and allows search by ID, username,
    and user’s first or last name.
    """
    list_filter = (('gender', admin.RelatedOnlyFieldListFilter),
                   'add_date')
    list_display_links = ('id', 'user')
    search_fields = ('id', 'user__username', 'user__first_name', 'user__last_name')
admin.site.register(Candidate, CandidateAdmin)


class ExpertiseAdmin(CustomModelAdminAllFields):
    """
    Admin interface for the `Expertise` model.

    Enables filtering by industry and searching by candidate ID and user details.
    """
    list_filter = (('industry', admin.RelatedOnlyFieldListFilter),)
    list_display_links = ('candidate',)
    search_fields = ('id', 'candidate__id', 'candidate__user__username', 'candidate__user__first_name')
admin.site.register(Expertise, ExpertiseAdmin)


class AcademicAreaAdmin(CustomModelAdminAllFields):
    """
    Admin interface for the `Academic_Area` model.

    Uses default configuration inherited from CustomModelAdminAllFields.
    """
    pass
admin.site.register(Academic_Area, AcademicAreaAdmin)


class AcademicStatusAdmin(CustomModelAdminAllFields):
    """
    Admin interface for the `Academic_Status` model.

    Uses default configuration inherited from CustomModelAdminAllFields.
    """
    pass
admin.site.register(Academic_Status, AcademicStatusAdmin)


class AcademicAdmin(CustomModelAdminAllFields):
    """
    Admin interface for the `Academic` model.

    Adds filters for degree and academic status, with search by candidate name and school.
    """
    list_filter = (('degree', admin.RelatedOnlyFieldListFilter),
                   ('status', admin.RelatedOnlyFieldListFilter))
    list_display_links = ('id', 'candidate')
    search_fields = ('id', 'candidate__first_name', 'candidate__last_name', 'school')
admin.site.register(Academic, AcademicAdmin)


class LanguageAdmin(CustomModelAdminAllFields):
    """
    Admin interface for the `Language` model.

    Uses default configuration inherited from CustomModelAdminAllFields.
    """
    pass
admin.site.register(Language, LanguageAdmin)


class CVLanguageAdmin(CustomModelAdminAllFields):
    """
    Admin interface for the `CV_Language` model.

    Filters by language and provides links to the candidate detail page.
    """
    list_filter = (('language', admin.RelatedOnlyFieldListFilter),)
    list_display_links = ('id', 'candidate')
admin.site.register(CV_Language, CVLanguageAdmin)

class CurriculumAdmin(CustomModelAdminAllFields):
    """
    Admin interface for the `Curriculum` model.

    Filters by last modified and add date, and allows search by candidate's first name.
    """
    list_filter = ('last_modified', 'add_date')
    list_display_links = ('id', 'candidate')
    search_fields = ('id', 'candidate__first_name')
admin.site.register(Curriculum, CurriculumAdmin)
