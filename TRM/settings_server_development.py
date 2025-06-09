# -*- coding: utf-8 -*-

from __future__ import absolute_import
import os.path
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_PATH = os.path.dirname(os.path.realpath(__file__))
protocol = 'http'
SITE_URL = 'http://demo.spotaxis.com'
SITE_SUFFIX = '.demo.spotaxis.com'

DATABASES = {
    'default': {
        'ENGINE': os.getenv('server_dev_db_engine'),  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.getenv('server_dev_db_name'),                      # Or path to database file if using sqlite3.
        'USER': os.getenv('server_dev_db_user'),                      # Not used with sqlite3.
        'PASSWORD': os.getenv('server_dev_db_password'),                  # Not used with sqlite3.
        'HOST': os.getenv('server_dev_db_host'),                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': os.getenv('server_dev_db_port'),                      # Set to empty string for default. Not used with sqlite3.
    }
}
SESSION_COOKIE_DOMAIN = '.example.com'
# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
# MEDIA_ROOT = ''
MEDIA_ROOT = '/var/www/demo/trm/TRM/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = 'http://demo.spotaxis.com/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/var/www/demo/trm/TRM/static/'

# Additional locations of static files
STATICFILES_DIRS = [
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/var/www/demo/trm/TRM/static/',
]
EMAIL_BACKEND = os.getenv('server_dev_email_backend') 
EMAIL_HOST = os.getenv('server_dev_email_host')
EMAIL_PORT = os.getenv('server_dev_email_port')
EMAIL_HOST_USER = os.getenv('server_dev_email_host_user')
EMAIL_HOST_PASSWORD = os.getenv('server_dev_email_password')
EMAIL_USE_TLS = os.getenv('server_dev_email_use_tls')
DEFAULT_FROM_EMAIL= os.getenv('sever_dev_default_from_email')
SERVER_EMAIL = os.getenv('sever_dev_server_email')
# EMAIL_HOST = 'email-smtp.us-west-2.amazonaws.com'
# EMAIL_HOST_USER = 'AKIAJJLTCMM766VE2HEQ'
# EMAIL_HOST_PASSWORD = 'AgxGkP/sAd6Z5pKCCJQblZF9ZEE+VbS+GdP09vTbnON1'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True

# SOCIAL_AUTH_FACEBOOK_KEY = '1419508698335934'
# SOCIAL_AUTH_FACEBOOK_SECRET = 'b8eb73b5bf1326fb91f7bac135b96475'

# FACEBOOK_APP_ID = '1474071052897625'
# FACEBOOK_APP_SECRET = 'bdac3b3fefdbd129bd7de7974f33bfc0'

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
logo_email = 'http://demo.spotaxis.com/static/img/logo/logo.png'

ALLOWED_HOSTS = [
    '*'
]

PAYPAL_MERCHANT_ID = os.getenv('server_dev_paypal_merchant_id')
PAYPAL_ACCESS_TOKEN = os.getenv('server_dev_paypal_access_token')
PAYPAL_CLIENT_ID = os.getenv('server_dev_paypal_client_id')
PAYPAL_APP_SECRET = os.getenv('server_dev_paypal_app_secret')
PAYPAL_ACCOUNT = os.getenv('server_dev_paypal_account')

import paypalrestsdk
paypalrestsdk.configure({
        'mode': 'sandbox', # sandbox or live
        'client_id': PAYPAL_CLIENT_ID,
        'client_secret': PAYPAL_APP_SECRET
    })


SOCIALAUTH_FACEBOOK_OAUTH_KEY = os.getenv('server_dev_facebook_oauth_key')
SOCIALAUTH_FACEBOOK_OAUTH_SECRET = ('server_dev_facebook_oauth_secret')

SOCIALAUTH_LINKEDIN_OAUTH_KEY = ('server_dev_linkedin_oauth_key')
SOCIALAUTH_LINKEDIN_OAUTH_SECRET = ('server_dev_linkedin_oauth_secret')

SOCIALAUTH_ANGEL_OAUTH_KEY = ('server_dev_angel_oauth_key')
SOCIALAUTH_ANGEL_OAUTH_SECRET = ('server_dev_angel_oauth_secret')

SOCIALAUTH_TWITTER_OAUTH_KEY = ('server_dev_twitter_oauth_key')
SOCIALAUTH_TWITTER_OAUTH_SECRET = ('server_dev_twitter_oauth_secret')

SOCIALAUTH_GOOGLEPLUS_OAUTH_KEY = ('server_dev_googleplus_oauth_key')
SOCIALAUTH_GOOGLEPLUS_OAUTH_SECRET = ('server_dev_googleplus_oauth_secret')

SOCIALAUTH_GITHUB_OAUTH_KEY = ('server_dev_github_oauth_key')
SOCIALAUTH_GITHUB_OAUTH_SECRET = ('server_dev_github_oauth_secret')

SOCIALAUTH_STACKOVERFLOW_OAUTH_KEY = ('server_dev_stackoverflow_oauth_key')
SOCIALAUTH_STACKOVERFLOW_OAUTH_SECRET = ('server_dev_stackoverflow_oauth_secret')
SOCIALAUTH_STACKOVERFLOW_OAUTH_REQUESTKEY = ('server_dev_stackoverflow_oauth_requestkey')
