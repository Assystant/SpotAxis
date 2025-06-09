# -*- coding: utf-8 -*-

from __future__ import absolute_import
import os.path
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_PATH = os.path.dirname(os.path.realpath(__file__))

protocol = 'http'

SITE_URL = 'http://spotaxis.com'
SITE_SUFFIX = '.spotaxis.com/'
DATABASES = {
    'default': {
        'ENGINE': os.getenv('local_db_engine'),  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.getenv('local_db_name'),                      # Or path to database file if using sqlite3.
        'USER': os.getenv('local_db_user'),                      # Not used with sqlite3.
        'PASSWORD': os.getenv('local_db_password'),                  # Not used with sqlite3.
        'HOST': os.getenv('local_db_host'),                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': os.getenv('local_db_port'),                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
# MEDIA_ROOT = ''
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = 'http://spotaxis.com/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# Additional locations of static files
STATICFILES_DIRS = [
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, 'static'),
]

EMAIL_HOST = os.getenv('local_email_host')
EMAIL_HOST_USER = os.getenv('local_email_host_user')
EMAIL_HOST_PASSWORD = os.getenv('local_email_host_password')
EMAIL_PORT = os.getenv('local_email_port')
EMAIL_USE_TLS = os.getenv('local_use_tls')

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# TRM | localhost
SOCIAL_AUTH_FACEBOOK_KEY = os.getenv('local_facebooK_key')
SOCIAL_AUTH_FACEBOOK_SECRET = os.getenv('local_facebook_secret')

# TRM | sandbox
# PAYPAL_MERCHANT_ID = 'DUGFVYW3LGYTW'
PAYPAL_MERCHANT_ID = os.getenv('local_paypal_merchant_id')
PAYPAL_ACCESS_TOKEN = os.getenv('local_paypal_access_token')
PAYPAL_CLIENT_ID = os.getenv('local_paypal_client_id')
PAYPAL_APP_SECRET = os.getenv('local_paypal_app_secret')
PAYPAL_ACCOUNT = os.getenv('local_paypal_account')

import paypalrestsdk
paypalrestsdk.configure({
        'mode': 'sandbox', # sandbox or live
        'client_id': PAYPAL_CLIENT_ID,
        'client_secret': PAYPAL_APP_SECRET
    })

# import braintree
# BRAINTREE_ACCESS_TOKEN = 'access_token$sandbox$42fgg8mwznb89ys2$81fa0749fc14faafabffe99ea319375b'
# BRAINTREE_ENVIRONMENT = braintree.Environment.Sandbox
# BRAINTREE_MERCHANT_ID = 'b2gkp8vzjgdtxsjz'
# BRAINTREE_PUBLIC_KEY = 'ww968rypmfzmzh6s'
# BRAINTREE_PRIVATE_KEY = 'db392287b6b973e76837559b9d03594d'
# braintree.Configuration.configure(
#     BRAINTREE_ENVIRONMENT,
#     BRAINTREE_MERCHANT_ID,
#     BRAINTREE_PUBLIC_KEY,
#     BRAINTREE_PRIVATE_KEY
# )
# TRM test
# FACEBOOK_APP_ID = '1474071052897625'
# FACEBOOK_APP_SECRET = 'bdac3b3fefdbd129bd7de7974f33bfc0'

SOCIALAUTH_FACEBOOK_OAUTH_KEY = os.getenv('local_facebook_oauth_key')
SOCIALAUTH_FACEBOOK_OAUTH_SECRET = os.getenv('local_facebook_oauth_secret')

SOCIALAUTH_LINKEDIN_OAUTH_KEY = os.getenv('local_linkedin_oauth_key')
SOCIALAUTH_LINKEDIN_OAUTH_SECRET = os.getenv('local_linkedin_oauth_secret')

SOCIALAUTH_ANGEL_OAUTH_KEY = os.getenv('local_angel_oauth_key')
SOCIALAUTH_ANGEL_OAUTH_SECRET = os.getenv('local_angel_oauth_secret')

SOCIALAUTH_TWITTER_OAUTH_KEY = os.getenv('local_twitter_oauth_key')
SOCIALAUTH_TWITTER_OAUTH_SECRET = os.getenv('local_twitter_oauth_secret')

SOCIALAUTH_GOOGLEPLUS_OAUTH_KEY = os.getenv('local_googleplus_oauth_key')
SOCIALAUTH_GOOGLEPLUS_OAUTH_SECRET = os.getenv('local_googleplus_oauth_secret')

SOCIALAUTH_GITHUB_OAUTH_KEY = os.getenv('local_github_oauth_key')
SOCIALAUTH_GITHUB_OAUTH_SECRET = os.getenv('local_github_oauth_secret')

SOCIALAUTH_STACKOVERFLOW_OAUTH_KEY = os.getenv('local_stackoverflow_oauth_key')
SOCIALAUTH_STACKOVERFLOW_OAUTH_SECRET = os.getenv('local_stackoverflow_oauth_secret')
SOCIALAUTH_STACKOVERFLOW_OAUTH_REQUESTKEY = os.getenv('local_stackoverflow_oatuh_requestkey')

logo_email = 'http://spotaxis.com/static/img/logo/logo.png'