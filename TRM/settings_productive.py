# -*- coding: utf-8 -*-

from __future__ import absolute_import
import os.path
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_PATH = os.path.dirname(os.path.realpath(__file__))

https = True

if https:
    protocol = 'https'
else:
    protocol = 'http'

SITE_URL = '%s://spotaxis.com' % protocol
SITE_SUFFIX = '.spotaxis.com/'

DATABASES = {
    'default': {
        'ENGINE': os.getenv('productive_db_engine'),  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.getenv('productive_db_name'),          # Or path to database file if using sqlite3.
        'USER': os.getenv('productive_db_user'),                # Not used with sqlite3.
        'PASSWORD': os.getenv('productive_db_password'),            # Not used with sqlite3.
        'HOST': os.getenv('productive_db_host'),                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': os.getenv('productive_db_host'),                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
# MEDIA_ROOT = ''
MEDIA_ROOT = '/var/www/spotaxis/trm/TRM/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "https://media.lawrence.com/media/", "https://example.com/media/"
MEDIA_URL = '%s://spotaxis.com/media/' % protocol

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/var/www/spotaxis/trm/TRM/static/'

# Additional locations of static files
STATICFILES_DIRS = [
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/var/www/spotaxis/trm/TRM/static/',
]
EMAIL_BACKEND = os.getenv('productive_email_backend')
EMAIL_HOST = os.getenv('productive_email_host')
EMAIL_PORT = os.getenv('productive_email_port')
EMAIL_HOST_USER = os.getenv('productive_email_host_user')
EMAIL_HOST_PASSWORD = os.getenv('productive_email_host_passw')
EMAIL_USE_TLS = os.getenv('productive_email_use_tls')
DEFAULT_FROM_EMAIL= os.getenv('productive_default_from_email')
SERVER_EMAIL = os.getenv('productive_server_email')

# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'contact.travelder@gmail.com'
# EMAIL_HOST_PASSWORD = 'qwerty123$'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True

#is this field unintentionally left active?
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# SPOTAXIS
# SOCIAL_AUTH_FACEBOOK_KEY = '1419508698335934'
# SOCIAL_AUTH_FACEBOOK_SECRET = 'b8eb73b5bf1326fb91f7bac135b96475'

# SPOTAXIS
# FACEBOOK_APP_ID = ''
# FACEBOOK_APP_SECRET = ''
PAYPAL_MERCHANT_ID = os.getenv('productive_paypal_merchant_id')
PAYPAL_ACCESS_TOKEN = os.getenv('productive_paypal_access_token')
PAYPAL_CLIENT_ID = os.getenv('productive_paypal_client_id')
PAYPAL_APP_SECRET = os.getenv('productive_paypal_app_secret')
PAYPAL_ACCOUNT = os.getenv('productive_paypal_account')

import paypalrestsdk
paypalrestsdk.configure({
        'mode': 'live', # sandbox or live
        'client_id': PAYPAL_CLIENT_ID,
        'client_secret': PAYPAL_APP_SECRET
    })

logo_email = '%s://spotaxis.com/static/img/logo/logo.png' % protocol

ALLOWED_HOSTS = [
    '*', # Allow domain and subdomains
]


SOCIALAUTH_FACEBOOK_OAUTH_KEY = os.getenv('productive_facebook_oauth_key')
SOCIALAUTH_FACEBOOK_OAUTH_SECRET = os.getenv('productive_facebook_oauth_secret')

SOCIALAUTH_LINKEDIN_OAUTH_KEY = os.getenv('productive_linkedin_oauth_key')
SOCIALAUTH_LINKEDIN_OAUTH_SECRET = os.getenv('productive_linkedin_oauth_secret')

SOCIALAUTH_ANGEL_OAUTH_KEY = os.getenv('productive_angel_oauth_key')
SOCIALAUTH_ANGEL_OAUTH_SECRET = os.getenv('productive_angel_oauth_secret')

SOCIALAUTH_TWITTER_OAUTH_KEY = os.getenv('productive_twitter_oauth_key')
SOCIALAUTH_TWITTER_OAUTH_SECRET = os.getenv('productive_twitter_oauth_secret')

SOCIALAUTH_GOOGLEPLUS_OAUTH_KEY = os.getenv('productive_googleplus_oauth_key')
SOCIALAUTH_GOOGLEPLUS_OAUTH_SECRET = os.getenv('productive_googleplus_oauth_secret')

SOCIALAUTH_GITHUB_OAUTH_KEY = os.getenv('productive_github_oauth_key')
SOCIALAUTH_GITHUB_OAUTH_SECRET = os.getenv('productive_github_oauth_secret')

SOCIALAUTH_STACKOVERFLOW_OAUTH_KEY = os.getenv('productive_stackoverflow_oauth_key')
SOCIALAUTH_STACKOVERFLOW_OAUTH_SECRET = os.getenv('productive_stackoverflow_oauth_secret')
SOCIALAUTH_STACKOVERFLOW_OAUTH_REQUESTKEY = os.getenv('productive_oauth_reuestkey')
