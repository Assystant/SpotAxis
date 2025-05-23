"""

Defines the configuration class for the 'companies' Django application.

This configuration class specifies metadata about the app, such as its name
and the human-readable verbose name. Django uses this class to configure
the app when it is included in INSTALLED_APPS.
"""


# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.apps import AppConfig


class CompaniesConfig(AppConfig):
    """
    Configuration class for the 'companies' app.

    Attributes:
        name (str): The full Python path to the app.
        verbose_name (str): A human-readable name for the app to be used
                            in the Django admin interface.
    """
    name = 'companies'
    verbose_name = 'Companies/Recruiters'
