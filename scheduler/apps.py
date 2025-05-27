
"""
Scheduler app configuration module.

Defines the application configuration class for the 'scheduler' Django app.
"""

from __future__ import absolute_import
from django.apps import AppConfig


class SchedulerConfig(AppConfig):
    """
    Configuration class for the 'scheduler' application.

    Attributes:
        name (str): The full Python path to the application.
    """
    name = 'scheduler'
