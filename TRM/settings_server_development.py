# -*- coding: utf-8 -*-

from __future__ import absolute_import
import os.path

PROJECT_PATH = os.path.dirname(os.path.realpath(__file__))
protocol = 'http'
SITE_URL = 'http://demo.spotaxis.com'
SITE_SUFFIX = '.demo.spotaxis.com'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'TRM_deployment_test',                      # Or path to database file if using sqlite3.
        'USER': 'TRM_user',                      # Not used with sqlite3.
        'PASSWORD': 'TRM_db_password',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
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
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL='SpotAxis <no-reply@spotaxis.com>'
SERVER_EMAIL = 'no-reply@spotaxis.com'
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

PAYPAL_MERCHANT_ID = 'XKMWAANJEJQ5U'
PAYPAL_ACCESS_TOKEN = 'access_token$sandbox$42fgg8mwznb89ys2$81fa0749fc14faafabffe99ea319375b'
PAYPAL_CLIENT_ID = 'AawWwBbC0IUBhU4sJ8I3aPzjBXIjJyzcAXYNSXxC1JCO4l6K_kr5TIU085cjwmOq34mg4pzCFyLkZeeK'
PAYPAL_APP_SECRET = 'EGkHxjwddqKnIDr6LUEPyY2IVqygyZxbf27M3RNhLUMEi1jUG4Wl864ZUfBHu0uM6V6fPjT_k5aSbgEG'
PAYPAL_ACCOUNT = 'contact@travelder.com'

import paypalrestsdk
paypalrestsdk.configure({
        'mode': 'sandbox', # sandbox or live
        'client_id': PAYPAL_CLIENT_ID,
        'client_secret': PAYPAL_APP_SECRET
    })


SOCIALAUTH_FACEBOOK_OAUTH_KEY = '745678155587072'
SOCIALAUTH_FACEBOOK_OAUTH_SECRET = '6fc2442d9a23bcfc104bb4fc27d5ccc1'

SOCIALAUTH_LINKEDIN_OAUTH_KEY = '81m81bg9hnd3jt'
SOCIALAUTH_LINKEDIN_OAUTH_SECRET = '3S8YXZEOIllmDsef'

SOCIALAUTH_ANGEL_OAUTH_KEY = ''
SOCIALAUTH_ANGEL_OAUTH_SECRET = ''

SOCIALAUTH_TWITTER_OAUTH_KEY = 'C6Jqc9i9Pr0whIcU18Fz8CNMQ'
SOCIALAUTH_TWITTER_OAUTH_SECRET = 'hNA7Xqf2gTXdUFmYQbvVXZOoM1HzeQn6PR1kduWMDXcdqvRdD3'

SOCIALAUTH_GOOGLEPLUS_OAUTH_KEY = '802095291346-o5eh8729ti70t1bbaj3h31qhmi99qitu.apps.googleusercontent.com'
SOCIALAUTH_GOOGLEPLUS_OAUTH_SECRET = 'ZrIkLhkTQ5ce84_geu6HxmGo'

SOCIALAUTH_GITHUB_OAUTH_KEY = 'fb93387bbc9f9ffcd2f7'
SOCIALAUTH_GITHUB_OAUTH_SECRET = '9e17b019a9d6fb3b6b843a4d462006ffb8d0dfa0'

SOCIALAUTH_STACKOVERFLOW_OAUTH_KEY = '8932'
SOCIALAUTH_STACKOVERFLOW_OAUTH_SECRET = 'qREi*HWy7c6xpMlnhSqjiQ(('
SOCIALAUTH_STACKOVERFLOW_OAUTH_REQUESTKEY = 'XDR1z6q3cmTZlOA**gbjPA(('
