# -*- coding: utf-8 -*-

from __future__ import absolute_import
from django.contrib import admin
from vacancies.models import Vacancy_Status, PubDate_Search, Employment_Experience, Salary_Type,\
    Vacancy, Postulate, Question, Vacancy_Files, Candidate_Fav, VacancyTags
from common.admin import CustomModelAdminAllFields


class VacancyStatusAdmin(CustomModelAdminAllFields):
    """Admin configuration for managing Vacancy_Status entries in the Django admin.
    
    Displays links for the 'id' and 'name' fields.
    """
    list_display_links = ('id', 'name')
admin.site.register(Vacancy_Status, VacancyStatusAdmin)


class PubDateSearchAdmin(CustomModelAdminAllFields):
    """Admin configuration for managing PubDate_Search entries.
    
    Displays links for the 'id' and 'name' fields.
    """
    list_display_links = ('id', 'name')
admin.site.register(PubDate_Search, PubDateSearchAdmin)


class EmploymentExperienceAdmin(CustomModelAdminAllFields):
    """Admin configuration for managing Employment_Experience entries.
    
    Displays links for the 'id' and 'name' fields.
    """
    list_display_links = ('id', 'name')
admin.site.register(Employment_Experience, EmploymentExperienceAdmin)


class SalaryTypeAdmin(CustomModelAdminAllFields):
    """Admin configuration for managing Salary_Type entries.
    
    Displays links for the 'id' and 'name' fields.
    """
    list_display_links = ('id', 'name')
admin.site.register(Salary_Type, SalaryTypeAdmin)


class VacancyAdmin(CustomModelAdminAllFields):
    """Admin configuration for managing Vacancy entries.
    
    Includes filters by status, employmentType, industry, and pub_date.
    Displays links for the 'id', 'company', and 'user' fields.
    Enables searching across various fields including description and emails.
    """
    list_filter = [
        # ('state', admin.RelatedOnlyFieldListFilter),
        ('status', admin.RelatedOnlyFieldListFilter),
        ('employmentType', admin.RelatedOnlyFieldListFilter),
        ('industry', admin.RelatedOnlyFieldListFilter),
        'pub_date'
    ]
    list_display_links = ('id', 'company', 'user')
    search_fields = ['id', 'employment', 'description', 'user__username', 'company__name', 'another_email', 'email']
admin.site.register(Vacancy, VacancyAdmin)


class PostulateAdmin(CustomModelAdminAllFields):
    """Admin configuration for managing Postulate entries.
    
    Filters by 'add_date'.
    Displays links for the 'id' and 'vacancy' fields.
    Supports searching by vacancy details and candidate names.
    """
    list_filter = ['add_date']
    list_display_links = ('id', 'vacancy')
    search_fields = ['vacancy__id', 'vacancy__employment', 'candidate__first_name', 'candidate__user__first_name']
admin.site.register(Postulate, PostulateAdmin)


# class PublicPostulateAdmin(CustomModelAdminAllFields):
#     list_filter = ['add_date']
#     list_display_links = ('id', 'vacancy')
#     search_fields = ('vacancy__id', 'vacancy__employment', 'full_name', 'email', 'file')
# admin.site.register(Public_Postulate, PublicPostulateAdmin)


class QuestionAdmin(CustomModelAdminAllFields):
    """Admin configuration for managing Question entries.
    
    Filters by 'question_date'.
    Displays links for the 'id' and 'vacancy' fields.
    Supports searching by related vacancy, user, question, and answer.
    """
    list_filter = ['question_date']
    list_display_links = ('id', 'vacancy')
    search_fields = ['vacancy__id', 'vacancy__employment', 'user__first_name', 'question', 'answer']
admin.site.register(Question, QuestionAdmin)


class CandidateFavAdmin(CustomModelAdminAllFields):
    """Admin configuration for managing Candidate_Fav entries.
    
    Filters by 'add_date'.
    Displays links for the 'id' and 'vacancy' fields.
    Enables searching by candidate and related vacancy information.
    """
    list_filter = ['add_date']
    list_display_links = ('id', 'vacancy')
    search_fields = ['vacancy__id', 'vacancy__employment', 'candidate__user__first_name', 'candidate__first_name']
admin.site.register(Candidate_Fav, CandidateFavAdmin)


class VacancyFilesAdmin(CustomModelAdminAllFields):
    """Admin configuration for managing Vacancy_Files entries.
    
    Filters by 'add_date'.
    Displays links for the 'id' and 'vacancy' fields.
    Enables searching by related vacancy and uploaded file name.
    """
    list_filter = ['add_date']
    list_display_links = ('id', 'vacancy')
    search_fields = ('vacancy__id', 'vacancy__employment', 'file')
admin.site.register(Vacancy_Files, VacancyFilesAdmin)


class VacancyTagsAdmin(CustomModelAdminAllFields):
    """Admin configuration for managing VacancyTags entries.
    
    Filters by related 'vacancy'.
    Displays links for the 'id' and 'vacancy' fields.
    Enables searching by vacancy and tag name.
    """
    list_filter = ['vacancy']
    list_display_links = ('id', 'vacancy')
    search_fields = ('vacancy__id', 'vacancy__employment', 'name')
admin.site.register(VacancyTags, VacancyTagsAdmin)
