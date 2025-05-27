"""
App configuration for the 'customField' Django application.

This module defines the configuration for the 'customField' app, allowing Django to identify
the app and apply any application-specific settings or behaviors during project initialization.
"""

from __future__ import absolute_import
from django.apps import AppConfig


class CustomfieldConfig(AppConfig):
    """
       Configuration class for the 'customField' application.

       Attributes:
           name (str): The name of the application. This should match the app directory name.
       """
    name = 'customField'
