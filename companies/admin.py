# # -*- coding: utf-8 -*-

from __future__ import absolute_import
from django.contrib import admin
from companies.models import Company_Industry, Company, Wallet, Recruiter, RecruiterInvitation, Ban, ExternalReferal
from common.admin import CustomModelAdminAllFields


class CompanyIndustryAdmin(CustomModelAdminAllFields):
    list_display_links = ('id', 'name')
    search_fields = ('name',)
admin.site.register(Company_Industry, CompanyIndustryAdmin)


# class CompanyAreaAdmin(CustomModelAdminAllFields):
#     list_filter = (('company_industry', admin.RelatedOnlyFieldListFilter),)
#     list_display_links = ('id', 'name')
#     search_fields = ('name', 'company_industry__name')
# admin.site.register(Company_Area, CompanyAreaAdmin)


class CompanyAdmin(CustomModelAdminAllFields):
    list_filter = (('industry', admin.RelatedOnlyFieldListFilter), 'add_date')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'social_name', 'url', 'phone')
admin.site.register(Company, CompanyAdmin)

class RecruiterAdmin(CustomModelAdminAllFields):
    # list_filter = (('industry', admin.RelatedOnlyFieldListFilter), 'add_date')
    # list_display_links = ('id', 'name')
    # search_fields = ('name', 'social_name', 'url', 'phone')
    pass
admin.site.register(Recruiter, RecruiterAdmin)

class BanAdmin(CustomModelAdminAllFields):
    # list_filter = (('industry', admin.RelatedOnlyFieldListFilter), 'add_date')
    # list_display_links = ('id', 'name')
    # search_fields = ('name', 'social_name', 'url', 'phone')
    pass
admin.site.register(Ban, BanAdmin)

class RecruiterInvitationAdmin(CustomModelAdminAllFields):
    # list_filter = (('industry', admin.RelatedOnlyFieldListFilter), 'add_date')
    # list_display_links = ('id', 'name')
    # search_fields = ('name', 'social_name', 'url', 'phone')
    pass
admin.site.register(RecruiterInvitation, RecruiterInvitationAdmin)


class WalletAdmin(CustomModelAdminAllFields):
    list_display_links = ('id', 'company')
    search_fields = ['company__name']
admin.site.register(Wallet, WalletAdmin)


# class RecommendationStatusAdmin(CustomModelAdminAllFields):
#     list_display_links = ('id', 'name')
# admin.site.register(Recommendation_Status, RecommendationStatusAdmin)


# class RecommendationsAdmin(CustomModelAdminAllFields):
#     list_display_links = ('id', 'to_company', 'from_company')
#     list_filter =(('status', admin.RelatedOnlyFieldListFilter), 'add_date')
#     search_fields = ('to_company__name', 'from_company__name')
# admin.site.register(Recommendations, RecommendationsAdmin)

class ExternalReferalAdmin(CustomModelAdminAllFields):
    list_display_links = ('id', 'company', 'name')
    search_fields = ['company__name', 'name']
admin.site.register(ExternalReferal, ExternalReferalAdmin)
