
"""
App configuration for the `candidates` application.

This module defines the configuration class used by Django to set up
and identify the `candidates` app within the project.
"""


# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.apps import AppConfig


class CandidatesConfig(AppConfig):
    """
    Configuration class for the `candidates` app.

    Attributes:
        name (str): The full Python path to the application.
        verbose_name (str): A human-readable name for the app to display in the admin site.
    """
    name = 'candidates'
    verbose_name = 'Candidates'
