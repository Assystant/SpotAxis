"""
Django admin configuration module for the common app.

This module configures the Django admin interface for all models in the common app.
It provides customized admin views and configurations for user management, profile management,
verification processes, and other core functionalities.

Classes:
    - CustomModelAdminAllFields: Base admin class that automatically displays all model fields
    - ProfileAdmin: Admin interface for Profile model
    - UserAdmin: Customized admin interface for User model
    - AccountVerificationAdmin: Admin interface for account verification
    - EmailVerificationAdmin: Admin interface for email verification
    - Various other model-specific admin classes
"""

# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from common.models import Profile, User, AccountVerification, EmailVerification, Employment_Type, Country,\
    Address, Degree, Marital_Status, Gender, Subdomain, SocialAuth

admin.site.unregister(Group)
# admin.site.unregister(Site)

class CustomModelAdminAllFields(admin.ModelAdmin):
    """
    Base admin class that automatically displays all fields of a model in the list view.
    
    This class serves as a foundation for other admin classes when all model fields
    should be displayed in the admin interface list view.
    """
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        self.actions_on_bottom = True
        super(CustomModelAdminAllFields, self).__init__(model, admin_site)


class ProfileAdmin(CustomModelAdminAllFields):
    """Admin interface for the Profile model, displaying all fields."""
    pass
admin.site.register(Profile, ProfileAdmin)


class UserAdmin(admin.ModelAdmin):
    """
    Customized admin interface for the User model.
    
    Provides detailed list display, filtering, and search capabilities for user management.
    """
    list_display = ('id', 'username', 'first_name', 'last_name', 'email', 'profile', 'logued_by', 'photo', 'is_active', 'is_staff', 'is_superuser', 'password', 'phone', 'phone_ext', 'cellphone', 'date_joined', 'last_login')
    list_filter = ('profile', 'logued_by', 'date_joined')
    list_display_links = ('id', 'username')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    actions_on_bottom = True
admin.site.register(User, UserAdmin)

class AccountVerificationAdmin(CustomModelAdminAllFields):
    """
    Admin interface for the AccountVerification model.
    
    Provides functionality to manage account verification processes.
    """
    list_display_links = ('id', 'user')
    search_fields = ['user__username']
admin.site.register(AccountVerification, AccountVerificationAdmin)

class EmailVerificationAdmin(CustomModelAdminAllFields):
    """
    Admin interface for the EmailVerification model.
    
    Manages email verification processes with filtering capabilities.
    """
    list_filter = ('is_approved', 'is_expired', 'expiration_date')
    list_display_links = ('id', 'user')
    search_fields = ('user__username', 'old_email', 'new_email')
admin.site.register(EmailVerification, EmailVerificationAdmin)

class CountryAdmin(CustomModelAdminAllFields):
    """Admin interface for the Country model with search capabilities."""
    list_display_links = ('id', 'name')
    search_fields = ('name',)
admin.site.register(Country, CountryAdmin)

class AddressAdmin(CustomModelAdminAllFields):
    """
    Admin interface for the Address model.
    
    Provides detailed address management with filtering and search capabilities.
    """
    list_display_links = ('id', 'street')
    list_filter = (('state', admin.RelatedOnlyFieldListFilter),)
    search_fields = ('street', 'postal_code', 'country__name', 'state__name', 'municipal__name')
admin.site.register(Address, AddressAdmin)

class DegreeAdmin(CustomModelAdminAllFields):
    """Admin interface for the Degree model."""
    list_display_links = ('id', 'name')
admin.site.register(Degree, DegreeAdmin)

class MaritalStatusAdmin(CustomModelAdminAllFields):
    """Admin interface for the Marital Status model."""
    list_display_links = ('id', 'name')
admin.site.register(Marital_Status, MaritalStatusAdmin)

class EmploymentTypeAdmin(CustomModelAdminAllFields):
    """Admin interface for the Employment Type model."""
    list_display_links = ('id', 'name')
admin.site.register(Employment_Type, EmploymentTypeAdmin)

class GenderAdmin(CustomModelAdminAllFields):
    """Admin interface for the Gender model."""
    list_display_links = ('id', 'name')
admin.site.register(Gender, GenderAdmin)

class SubdomainAdmin(CustomModelAdminAllFields):
    """Admin interface for the Subdomain model."""
    list_display_links = ('cname', 'slug')
admin.site.register(Subdomain, SubdomainAdmin)

class SocialAuthAdmin(admin.ModelAdmin):
    """
    Admin interface for the SocialAuth model.
    
    Manages social authentication records with filtering and search capabilities.
    """
    list_display = ('id','user','identifier','social_code')
    list_display_links = ('identifier',)
    list_filter = ('social_code',)
    search_fields = ('user__first_name','user__last_name', 'user__username', 'user__email')
    actions_on_bottom = True
admin.site.register(SocialAuth, SocialAuthAdmin)