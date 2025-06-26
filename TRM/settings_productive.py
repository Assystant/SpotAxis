# -*- coding: utf-8 -*-

from __future__ import absolute_import
import os.path

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
        'ENGINE': 'django.db.backends.mysql',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'TRM_production',          # Or path to database file if using sqlite3.
        'USER': 'TRM_user',                # Not used with sqlite3.
        'PASSWORD': 'TRM_db_password',            # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
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
#EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL='SpotAxis <noreply@mail.spotaxis.com>'
SERVER_EMAIL = 'SpotAxis <server@mail.spotaxis.com>'

# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'contact.travelder@gmail.com'
# EMAIL_HOST_PASSWORD = 'qwerty123$'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True


#DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# SPOTAXIS
# SOCIAL_AUTH_FACEBOOK_KEY = '1419508698335934'
# SOCIAL_AUTH_FACEBOOK_SECRET = 'b8eb73b5bf1326fb91f7bac135b96475'

# SPOTAXIS
# FACEBOOK_APP_ID = ''
# FACEBOOK_APP_SECRET = ''
PAYPAL_MERCHANT_ID = 'XKMWAANJEJQ5U'
PAYPAL_ACCESS_TOKEN = 'access_token$sandbox$42fgg8mwznb89ys2$81fa0749fc14faafabffe99ea319375b'
PAYPAL_CLIENT_ID = 'AXlssOdyNmxlCzwD67yW7GDIXkynUdUMMaGOkCcQFmWIvdWz4dM_K4JYnh4926J7_psWxdjS0_fMchDD'
PAYPAL_APP_SECRET = 'EF2MmDhcbBzk5sU2oUSkuDBVec8xbDfubOyLHudg3Ca06OI8qMSJCe4NuV--5tpWOcz-Hbh94fpBKe-Q'
PAYPAL_ACCOUNT = 'contact@travelder.com'

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
