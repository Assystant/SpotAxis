"""It specifies metadata such as the app name and the human-readable verbose name, which appears in the Django admin interface."""

# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.apps import AppConfig


class CompaniesConfig(AppConfig):
    """
    Configuration class for the 'companies' app.

    Defines the app's label and verbose name as displayed in the Django admin interface.

    Attributes:
        name (str): The full Python path to the app.
        verbose_name (str): A human-readable name for the app.

    Inherits from:
        django.apps.AppConfig
    """
    name = 'companies'
    verbose_name = 'Companies/Recruiters'
