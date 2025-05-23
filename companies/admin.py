
# -*- coding: utf-8 -*-

"""

Registers Django admin interfaces for models in the 'companies' app.

This module customizes how models like Company, Recruiter, Wallet, and others 
are displayed and managed through the Django admin interface. It uses a shared 
base admin class (`CustomModelAdminAllFields`) from the 'common' module to 
ensure consistency in field rendering across models.

Models Registered:
    - Company_Industry
    - Company
    - Recruiter
    - Ban
    - RecruiterInvitation
    - Wallet
    - ExternalReferal

Each admin class may define search fields, list filters, and display links 
to enhance admin usability.
"""


# # -*- coding: utf-8 -*-

from __future__ import absolute_import
from django.contrib import admin
from companies.models import Company_Industry, Company, Wallet, Recruiter, RecruiterInvitation, Ban, ExternalReferal
from common.admin import CustomModelAdminAllFields


class CompanyIndustryAdmin(CustomModelAdminAllFields):
    """
    Admin interface configuration for the Company_Industry model.

    Allows admin users to search industries by name and provides
    clickable links to industry detail pages via ID and name.
    """
    list_display_links = ('id', 'name')
    search_fields = ('name',)
admin.site.register(Company_Industry, CompanyIndustryAdmin)


# class CompanyAreaAdmin(CustomModelAdminAllFields):
#     list_filter = (('company_industry', admin.RelatedOnlyFieldListFilter),)
#     list_display_links = ('id', 'name')
#     search_fields = ('name', 'company_industry__name')
# admin.site.register(Company_Area, CompanyAreaAdmin)


class CompanyAdmin(CustomModelAdminAllFields):
    """
    Admin interface for managing Company instances.

    Adds filters by industry and add date, and allows searching
    by name, social name, URL, and phone number.
    """
    list_filter = (('industry', admin.RelatedOnlyFieldListFilter), 'add_date')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'social_name', 'url', 'phone')
admin.site.register(Company, CompanyAdmin)

class RecruiterAdmin(CustomModelAdminAllFields):
    """
    Admin interface for managing Recruiter instances.

    Currently uses default behavior from CustomModelAdminAllFields
    without additional customization.
    """
    # list_filter = (('industry', admin.RelatedOnlyFieldListFilter), 'add_date')
    # list_display_links = ('id', 'name')
    # search_fields = ('name', 'social_name', 'url', 'phone')
    pass
admin.site.register(Recruiter, RecruiterAdmin)

class BanAdmin(CustomModelAdminAllFields):
    """
    Admin interface for managing Ban records.

    Currently uses default behavior from CustomModelAdminAllFields
    without additional customization.
    """
    # list_filter = (('industry', admin.RelatedOnlyFieldListFilter), 'add_date')
    # list_display_links = ('id', 'name')
    # search_fields = ('name', 'social_name', 'url', 'phone')
    pass
admin.site.register(Ban, BanAdmin)

class RecruiterInvitationAdmin(CustomModelAdminAllFields):
    """
    Admin interface for managing RecruiterInvitation entries.

    Currently uses default behavior from CustomModelAdminAllFields
    without additional customization.
    """
    # list_filter = (('industry', admin.RelatedOnlyFieldListFilter), 'add_date')
    # list_display_links = ('id', 'name')
    # search_fields = ('name', 'social_name', 'url', 'phone')
    pass
admin.site.register(RecruiterInvitation, RecruiterInvitationAdmin)


class WalletAdmin(CustomModelAdminAllFields):
    """
    Admin interface for managing Wallet instances.

    Enables search by related company name and sets clickable fields
    for ID and associated company.
    """
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
    """
    Admin interface for managing ExternalReferal instances.

    Allows searching by both company name and referral name,
    and sets the ID, company, and name fields as clickable.
    """
    list_display_links = ('id', 'company', 'name')
    search_fields = ['company__name', 'name']
admin.site.register(ExternalReferal, ExternalReferalAdmin)
