"""This module initializes the 'companies' Django app by specifying the default
application configuration class. When Django starts, it uses this configuration
to set up the app's behavior, such as signals and settings customization.

Attributes:
    default_app_config (str): A dotted path to the CompaniesConfig class,
    which is used by Django to configure the app.

Usage:
    This file allows Django to recognize and apply the custom app configuration
    defined in companies/apps.py when the application is included in INSTALLED_APPS.
"""


# -*- coding: utf-8 -*-

default_app_config = 'companies.apps.CompaniesConfig'
