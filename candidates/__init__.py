"""
This module sets the default application configuration for the 'candidates' Django app.

By specifying `default_app_config`, Django will use the custom configuration class
`CandidatesConfig` defined in `candidates/apps.py` instead of the default AppConfig.

This allows the app to define ready() hooks, application-specific settings,
signal registration, or other custom startup logic.

Attributes:
    default_app_config (str): Path to the custom application configuration class.
"""

# -*- coding: utf-8 -*-

default_app_config = 'candidates.apps.CandidatesConfig'
