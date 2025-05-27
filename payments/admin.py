# -*- coding: utf-8 -*-

from __future__ import absolute_import
from django.contrib import admin
from payments.models import *
from common.admin import CustomModelAdminAllFields

"""
Django admin configuration for the 'payments' app.

This module defines customized admin interfaces for models such as
ServiceCategory, Services, Package, PriceSlab, Subscription, Transactions,
Discount, and Discount_Usage.

Modules Used:
    - __future__.absolute_import: Ensures consistent import behavior across Python 2 and 3.
    - django.contrib.admin: Django’s admin framework for model representation.
    - payments.models: Contains the model definitions used in the payments module.
    - common.admin.CustomModelAdminAllFields: A custom admin class providing auto display of all fields.
"""

class ServiceCategoryAdmin(CustomModelAdminAllFields):
    """
    Admin interface for the ServiceCategory model.

    Attributes:
        list_display_links (tuple): Fields that are clickable in the list display.
    """
    list_display_links = ('id', 'name')
admin.site.register(ServiceCategory, ServiceCategoryAdmin)


class ServicesAdmin(CustomModelAdminAllFields):
    """
    Admin interface for the Services model.

    Attributes:
        list_filter (tuple): Fields used for filtering in the admin.
        list_display_links (tuple): Clickable fields in list view.
        search_fields (tuple): Fields used for search functionality.
    """
    list_filter = (('category', admin.RelatedOnlyFieldListFilter),)
    list_display_links = ('id', 'name', 'category', 'codename')
    search_fields = ('category__name', 'category__codename')
admin.site.register(Services, ServicesAdmin)


class PackageAdmin(CustomModelAdminAllFields):
    """
    Admin interface for the Package model.

    Attributes:
        list_filter (tuple): Filters for related services and user limits.
        list_display_links (tuple): Clickable fields in list display.
        search_fields (tuple): Fields for search functionality.
    """
    list_filter = (('services', admin.RelatedOnlyFieldListFilter),
                   'free_users',
                   'max_users')
    list_display_links = ('id', 'free_users', 'max_users')
    search_fields = ('services__name', 'services__codename',)
admin.site.register(Package, PackageAdmin)

class PriceSlabAdmin(CustomModelAdminAllFields):
    """
    Admin interface for the Services model.

    Attributes:
        list_filter (tuple): Fields used for filtering in the admin.
        list_display_links (tuple): Clickable fields in list view.
        search_fields (tuple): Fields used for search functionality.
    """
    list_filter = (('currency', admin.RelatedOnlyFieldListFilter),
                   'slab_period',
                   'expiry_period',
                   ('package', admin.RelatedOnlyFieldListFilter))
    list_display_links = ('id', 'currency', 'package', 'slab_period', 'amount')
    search_fields = ('currency__name', 'currency__codename', 'package__name')
admin.site.register(PriceSlab, PriceSlabAdmin)

class SubscriptionAdmin(CustomModelAdminAllFields):
    """
    Admin interface for the Subscription model.

    Attributes:
        list_filter (tuple): Filters based on company and price slab.
        list_display_links (tuple): Clickable fields in the list display.
        search_fields (tuple): Fields used to search for subscription details.
    """
    list_filter = (('company', admin.RelatedOnlyFieldListFilter),
                   ('price_slab', admin.RelatedOnlyFieldListFilter))
    list_display_links = ('id', 'price_slab', 'company', 'added_users', 'expiry')
    search_fields = ('company__name', 'price_slab__currency__name', 'price_slab__currency__codename')
admin.site.register(Subscription, SubscriptionAdmin)

class TransactionsAdmin(CustomModelAdminAllFields):
    """
    Admin interface for the Transactions model.

    Attributes:
        list_filter (tuple): Filters by user, company, transaction type, and timestamp.
        list_display_links (tuple): Clickable fields in the list display.
        search_fields (tuple): Fields used for transaction-related searches.
    """
    list_filter = (('user', admin.RelatedOnlyFieldListFilter),
    				('company', admin.RelatedOnlyFieldListFilter),
                   'type',
                   'timestamp',
                   'amount')
    list_display_links = ('id', 'user', 'company', 'timestamp', 'amount', 'type')
    search_fields = ('user__username', 'user__first_name', 'reason', 'company__name', 'company__social_name')
admin.site.register(Transactions, TransactionsAdmin)

class Discount_UsageInline(admin.TabularInline):
    """
    Inline admin class for displaying Discount_Usage within the Discount admin form.

    Attributes:
        model (Model): The model to be edited inline.
        extra (int): Number of extra blank forms shown by default.
    """
    model = Discount_Usage
    extra = 1

class Discount_UsageAdmin(CustomModelAdminAllFields):
    """
    Admin interface for the Discount_Usage model.
    Inherits all field rendering behavior from CustomModelAdminAllFields.
    """
    model = Discount_Usage
    pass
class DiscountAdmin(CustomModelAdminAllFields):
    """
    Admin interface for the Discount model.

    Attributes:
        inlines (tuple): Inline model classes to include in this admin.
    """
    inlines = (Discount_UsageInline,)
    pass
    # list_display_links = ('id', 'name')
admin.site.register(Discount, DiscountAdmin)
