# -*- coding: utf-8 -*-

from __future__ import absolute_import
from django.contrib import admin
from payments.models import *
from common.admin import CustomModelAdminAllFields


class ServiceCategoryAdmin(CustomModelAdminAllFields):
    list_display_links = ('id', 'name')
admin.site.register(ServiceCategory, ServiceCategoryAdmin)


class ServicesAdmin(CustomModelAdminAllFields):
    list_filter = (('category', admin.RelatedOnlyFieldListFilter),)
    list_display_links = ('id', 'name', 'category', 'codename')
    search_fields = ('category__name', 'category__codename')
admin.site.register(Services, ServicesAdmin)


class PackageAdmin(CustomModelAdminAllFields):
    list_filter = (('services', admin.RelatedOnlyFieldListFilter),
                   'free_users',
                   'max_users')
    list_display_links = ('id', 'free_users', 'max_users')
    search_fields = ('services__name', 'services__codename',)
admin.site.register(Package, PackageAdmin)
class PriceSlabAdmin(CustomModelAdminAllFields):
    list_filter = (('currency', admin.RelatedOnlyFieldListFilter),
                   'slab_period',
                   'expiry_period',
                   ('package', admin.RelatedOnlyFieldListFilter))
    list_display_links = ('id', 'currency', 'package', 'slab_period', 'amount')
    search_fields = ('currency__name', 'currency__codename', 'package__name')
admin.site.register(PriceSlab, PriceSlabAdmin)
class SubscriptionAdmin(CustomModelAdminAllFields):
    list_filter = (('company', admin.RelatedOnlyFieldListFilter),
                   ('price_slab', admin.RelatedOnlyFieldListFilter))
    list_display_links = ('id', 'price_slab', 'company', 'added_users', 'expiry')
    search_fields = ('company__name', 'price_slab__currency__name', 'price_slab__currency__codename')
admin.site.register(Subscription, SubscriptionAdmin)
class TransactionsAdmin(CustomModelAdminAllFields):
    list_filter = (('user', admin.RelatedOnlyFieldListFilter),
    				('company', admin.RelatedOnlyFieldListFilter),
                   'type',
                   'timestamp',
                   'amount')
    list_display_links = ('id', 'user', 'company', 'timestamp', 'amount', 'type')
    search_fields = ('user__username', 'user__first_name', 'reason', 'company__name', 'company__social_name')
admin.site.register(Transactions, TransactionsAdmin)

class Discount_UsageInline(admin.TabularInline):
    model = Discount_Usage
    extra = 1

class Discount_UsageAdmin(CustomModelAdminAllFields):
  model = Discount_Usage
  pass
class DiscountAdmin(CustomModelAdminAllFields):
  inlines = (Discount_UsageInline,)
  pass
    # list_display_links = ('id', 'name')
admin.site.register(Discount, DiscountAdmin)
