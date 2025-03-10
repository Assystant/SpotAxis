# -*- coding: utf-8 -*-

from __future__ import absolute_import
from django.contrib import admin
from vacancies.models import Vacancy_Status, PubDate_Search, Employment_Experience, Salary_Type,\
    Vacancy, Postulate, Question, Vacancy_Files, Candidate_Fav, VacancyTags
from common.admin import CustomModelAdminAllFields


class VacancyStatusAdmin(CustomModelAdminAllFields):
    list_display_links = ('id', 'name')
admin.site.register(Vacancy_Status, VacancyStatusAdmin)


class PubDateSearchAdmin(CustomModelAdminAllFields):
    list_display_links = ('id', 'name')
admin.site.register(PubDate_Search, PubDateSearchAdmin)


class EmploymentExperienceAdmin(CustomModelAdminAllFields):
    list_display_links = ('id', 'name')
admin.site.register(Employment_Experience, EmploymentExperienceAdmin)


class SalaryTypeAdmin(CustomModelAdminAllFields):
    list_display_links = ('id', 'name')
admin.site.register(Salary_Type, SalaryTypeAdmin)


class VacancyAdmin(CustomModelAdminAllFields):
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
    list_filter = ['question_date']
    list_display_links = ('id', 'vacancy')
    search_fields = ['vacancy__id', 'vacancy__employment', 'user__first_name', 'question', 'answer']
admin.site.register(Question, QuestionAdmin)


class CandidateFavAdmin(CustomModelAdminAllFields):
    list_filter = ['add_date']
    list_display_links = ('id', 'vacancy')
    search_fields = ['vacancy__id', 'vacancy__employment', 'candidate__user__first_name', 'candidate__first_name']
admin.site.register(Candidate_Fav, CandidateFavAdmin)


class VacancyFilesAdmin(CustomModelAdminAllFields):
    list_filter = ['add_date']
    list_display_links = ('id', 'vacancy')
    search_fields = ('vacancy__id', 'vacancy__employment', 'file')
admin.site.register(Vacancy_Files, VacancyFilesAdmin)


class VacancyTagsAdmin(CustomModelAdminAllFields):
    list_filter = ['vacancy']
    list_display_links = ('id', 'vacancy')
    search_fields = ('vacancy__id', 'vacancy__employment', 'name')
admin.site.register(VacancyTags, VacancyTagsAdmin)
