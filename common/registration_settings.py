"""
Registration settings for the common app.

This module defines configuration settings for the user registration process.
It may include settings for:
- Account activation
- Email verification
- Registration timeouts
- Password policies
"""
# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

DOUBLE_CHECK_EMAIL = getattr(
    settings, 'COMMON_DOUBLE_CHECK_EMAIL', False)

CHECK_UNIQUE_EMAIL = getattr(
    settings, 'COMMON_CHECK_UNIQUE_EMAIL', True)

DOUBLE_CHECK_PASSWORD = getattr(
    settings, 'COMMON_DOUBLE_CHECK_PASSWORD', True)

REGISTRATION_FULLNAME = getattr(
    settings, 'COMMON_REGISTRATION_FULLNAME', True)

# Only use Email field on the form
EMAIL_ONLY = getattr(
    settings, 'COMMON_EMAIL_ONLY', False)

# Automatically log in the user upon registration
AUTO_LOGIN = getattr(
    settings, 'COMMON_AUTO_LOGIN', False)

# Allows user to more easily control where registrations land
REGISTRATION_REDIRECT = getattr(
    settings,
    'COMMON_REDIRECT_ON_REGISTRATION',
    'common_registration_complete'
)

USE_ACCOUNT_VERIFICATION = getattr(
    settings, 'COMMON_USE_ACCOUNT_VERIFICATION', True)

# These settings together make no sense
if USE_ACCOUNT_VERIFICATION and AUTO_LOGIN:
    raise ImproperlyConfigured("You cannot use autologin with account verification")

ACCOUNT_VERIFICATION_DAYS = getattr(
    settings, 'COMMON_ACCOUNT_VERIFICATION_DAYS', 2)

EMAIL_VERIFICATION_DAYS = getattr(
    settings, 'COMMON_EMAIL_VERIFICATION_DAYS', 2)

EMAIL_VERIFICATION_DONE_URL = getattr(
    settings, 'COMMON_EMAIL_VERIFICATION_DONE_URL',
    'common_email_change_complete')

PROFILE_ALLOW_EMAIL_CHANGE = getattr(
    settings, 'COMMON_PROFILE_ALLOW_EMAIL_CHANGE', False)

if PROFILE_ALLOW_EMAIL_CHANGE and CHECK_UNIQUE_EMAIL:
    raise ImproperlyConfigured(
        'COMMON_PROFILE_ALLOW_EMAIL_CHANGE cannot be activated '
        'when COMMON_CHECK_UNIQUE_EMAIL is active.')

if (PROFILE_ALLOW_EMAIL_CHANGE
    and 'common.contrib.emailverification' in settings.INSTALLED_APPS):
    raise ImproperlyConfigured(
        'COMMON_PROFILE_ALLOW_EMAIL_CHANGE cannot be activated '
        'when `common.contrib.emailverification` is used.')
