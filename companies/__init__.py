
"""
This module initializes the Django application configuration for the 'companies' app.
It sets the default app configuration class to `CompaniesConfig`, which is defined
in the `companies.apps` module. By specifying this, Django will use the custom 
configuration class instead of the default AppConfig when loading the application.

Attributes:
    default_app_config (str): The dotted path to the custom application configuration class.
"""
# -*- coding: utf-8 -*-

default_app_config = 'companies.apps.CompaniesConfig'
