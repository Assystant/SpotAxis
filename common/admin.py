# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from common.models import Profile, User, AccountVerification, EmailVerification, Employment_Type, Country,\
    Address, Degree, Marital_Status, Gender, Subdomain, SocialAuth

admin.site.unregister(Group)
# admin.site.unregister(Site)

class CustomModelAdminAllFields(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        self.actions_on_bottom = True
        super(CustomModelAdminAllFields, self).__init__(model, admin_site)


class ProfileAdmin(CustomModelAdminAllFields):
    pass
admin.site.register(Profile, ProfileAdmin)


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'email', 'profile', 'logued_by', 'photo', 'is_active', 'is_staff', 'is_superuser', 'password', 'phone', 'phone_ext', 'cellphone', 'date_joined', 'last_login')
    list_filter = ('profile', 'logued_by', 'date_joined')
    list_display_links = ('id', 'username')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    actions_on_bottom = True
admin.site.register(User, UserAdmin)

class AccountVerificationAdmin(CustomModelAdminAllFields):
    list_display_links = ('id', 'user')
    search_fields = ['user__username']
admin.site.register(AccountVerification, AccountVerificationAdmin)

class EmailVerificationAdmin(CustomModelAdminAllFields):
    list_filter = ('is_approved', 'is_expired', 'expiration_date')
    list_display_links = ('id', 'user')
    search_fields = ('user__username', 'old_email', 'new_email')
admin.site.register(EmailVerification, EmailVerificationAdmin)

class CountryAdmin(CustomModelAdminAllFields):
    list_display_links = ('id', 'name')
    search_fields = ('name',)
admin.site.register(Country, CountryAdmin)

class AddressAdmin(CustomModelAdminAllFields):
    list_display_links = ('id', 'street')
    list_filter = (('state', admin.RelatedOnlyFieldListFilter),)
    search_fields = ('street', 'postal_code', 'country__name', 'state__name', 'municipal__name')
admin.site.register(Address, AddressAdmin)

class DegreeAdmin(CustomModelAdminAllFields):
    list_display_links = ('id', 'name')
admin.site.register(Degree, DegreeAdmin)

class MaritalStatusAdmin(CustomModelAdminAllFields):
    list_display_links = ('id', 'name')
admin.site.register(Marital_Status, MaritalStatusAdmin)

class EmploymentTypeAdmin(CustomModelAdminAllFields):
    list_display_links = ('id', 'name')
admin.site.register(Employment_Type, EmploymentTypeAdmin)

class GenderAdmin(CustomModelAdminAllFields):
    list_display_links = ('id', 'name')
admin.site.register(Gender, GenderAdmin)

class SubdomainAdmin(CustomModelAdminAllFields):
    list_display_links = ('cname', 'slug')
admin.site.register(Subdomain, SubdomainAdmin)

class SocialAuthAdmin(admin.ModelAdmin):
    list_display = ('id','user','identifier','social_code')
    list_display_links = ('identifier',)
    list_filter = ('social_code',)
    search_fields = ('user__first_name','user__last_name', 'user__username', 'user__email')
    actions_on_bottom = True
admin.site.register(SocialAuth, SocialAuthAdmin)