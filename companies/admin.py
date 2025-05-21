"""
This module defines custom Django admin configurations for models in the companies app.
It uses a shared CustomModelAdminAllFields base class to configure admin interfaces for models such as Company, Wallet, Recruiter, and others. 
The admin classes define custom behavior for display, filtering, and search functionality to improve data management in the Django admin interface.
"""

# # -*- coding: utf-8 -*-

from __future__ import absolute_import
from django.contrib import admin
from companies.models import Company_Industry, Company, Wallet, Recruiter, RecruiterInvitation, Ban, ExternalReferal
from common.admin import CustomModelAdminAllFields


class CompanyIndustryAdmin(CustomModelAdminAllFields):
    """
    Admin configuration for the Company_Industry model.

    This class customizes the Django admin interface by specifying:
    - Fields used to link to the object detail view.
    - Fields that are searchable.

    Inherits from:
        CustomModelAdminAllFields (common.admin): Base class with default admin settings.
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
    Admin configuration for the Company model.

    Customizes the admin interface to:
    - Filter companies by industry and addition date.
    - Make certain fields clickable to access details.
    - Enable search functionality for various text fields.

    Inherits from:
        CustomModelAdminAllFields (common.admin)
    """

    list_filter = (('industry', admin.RelatedOnlyFieldListFilter), 'add_date')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'social_name', 'url', 'phone')
admin.site.register(Company, CompanyAdmin)

class RecruiterAdmin(CustomModelAdminAllFields):
    """
    Admin configuration for the Recruiter model.

    Currently uses default settings inherited from the base class.

    Inherits from:
        CustomModelAdminAllFields (common.admin)
    """
    # list_filter = (('industry', admin.RelatedOnlyFieldListFilter), 'add_date')
    # list_display_links = ('id', 'name')
    # search_fields = ('name', 'social_name', 'url', 'phone')
    pass
admin.site.register(Recruiter, RecruiterAdmin)

class BanAdmin(CustomModelAdminAllFields):
    """
    Admin configuration for the Ban model.

    Currently uses default settings inherited from the base class.

    Inherits from:
        CustomModelAdminAllFields (common.admin)
    """
    # list_filter = (('industry', admin.RelatedOnlyFieldListFilter), 'add_date')
    # list_display_links = ('id', 'name')
    # search_fields = ('name', 'social_name', 'url', 'phone')
    pass
admin.site.register(Ban, BanAdmin)

class RecruiterInvitationAdmin(CustomModelAdminAllFields):
    """
    Admin configuration for the RecruiterInvitation model.

    Currently uses default settings inherited from the base class.

    Inherits from:
        CustomModelAdminAllFields (common.admin)
    """
    # list_filter = (('industry', admin.RelatedOnlyFieldListFilter), 'add_date')
    # list_display_links = ('id', 'name')
    # search_fields = ('name', 'social_name', 'url', 'phone')
    pass
admin.site.register(RecruiterInvitation, RecruiterInvitationAdmin)


class WalletAdmin(CustomModelAdminAllFields):
    """
    Admin configuration for the Wallet model.

    Customizes the admin interface to:
    - Set the clickable links to the wallet's ID and related company.
    - Enable search by the company name.

    Inherits from:
        CustomModelAdminAllFields (common.admin)
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
    Admin configuration for the ExternalReferal model.

    Customizes the admin interface to:
    - Allow linking via the ID, associated company, and referal name.
    - Enable searching by company name and referal name.

    Inherits from:
        CustomModelAdminAllFields (common.admin)
    """
    list_display_links = ('id', 'company', 'name')
    search_fields = ['company__name', 'name']
admin.site.register(ExternalReferal, ExternalReferalAdmin)
