# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    """
    Configuration class for the 'payments' application.

    This class inherits from Django's AppConfig and defines the metadata 
    for the payments app. It is used by Django to configure and initialize 
    application-specific settings.

    Attributes:
        name (str): The full Python path to the application.
        verbose_name (str): The human-readable name for the application used in the admin site.

    Modules Used:
        - `__future__.absolute_import`: Ensures consistent import behavior between Python 2 and 3.
        - `django.apps.AppConfig`: Base class for configuring Django applications.
    """
    name = 'payments'
    verbose_name = 'Payments/Services'
