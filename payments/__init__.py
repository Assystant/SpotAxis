# -*- coding: utf-8 -*-

"""
App initialization for the 'payments' Django app.

This file sets the default application configuration for the payments module.

Attributes:
    default_app_config (str): Path to the application configuration class. This tells Django
    to use the custom AppConfig class 'PaymentsConfig' defined in 'payments/apps.py'.
"""

default_app_config = 'payments.apps.PaymentsConfig'
