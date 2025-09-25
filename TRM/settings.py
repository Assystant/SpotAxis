# -*- coding: utf-8 -*-

from __future__ import absolute_import
import os
from dotenv import load_dotenv
import paypalrestsdk

load_dotenv()

PROJECT_NAME = 'SpotAxis'
PROJECT_PATH = os.path.dirname(os.path.realpath(__file__))

ADMINS = (('Saket', 'saket@spotaxis.com'), ('Holesh', 'holesh@spotaxis.com'))
MANAGERS = ADMINS

ENVIRONMENT = os.getenv('ENVIRONMENT')

DEBUG = ENVIRONMENT in ['local_development', 'server_development']

#ALLOWED_HOSTS = os.getenv('allowed_hosts')
ALLOWED_HOSTS = ['*']
SESSION_COOKIE_DOMAIN = os.getenv('session_cookie_domain')
TIME_ZONE = os.getenv('TIME_ZONE', 'Asia/Kolkata')
LANGUAGE_CODE = 'en-IN'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

if ENVIRONMENT == 'local_development':
    HOSTED_URL = "http://spotaxis.com"
    ROOT_DOMAIN = "spotaxis"
elif ENVIRONMENT == 'server_development':
    HOSTED_URL = "http://demo.spotaxis.com"
    ROOT_DOMAIN = "demo.spotaxis"
elif ENVIRONMENT == 'productive':
    HOSTED_URL = "https://spotaxis.com"
    ROOT_DOMAIN = "spotaxis"
else:
    HOSTED_URL = "http://spotaxis.com"
    ROOT_DOMAIN = "spotaxis"

gettext = lambda s: s
LANGUAGES = (('en', gettext('English')),) 

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


STATIC_URL = '/static/'
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.getenv('SECRET_KEY')

# Change the defautl Serialization in Django 1.6 form Json to Pickle
#SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

ROOT_URLCONF = 'TRM.urls'
SUBDOMAIN_URLCONF = 'TRM.subdomain_urls'
SUPPORT_URLCONF = 'TRM.support_urls'
BLOG_URLCONF = 'TRM.blog_urls'
WSGI_APPLICATION = 'TRM.wsgi.application'

AUTH_USER_MODEL = 'common.User'
LOGIN_URL = '/login/'
LOGIN_ERROR_URL = '/login/'
LOGIN_REDIRECT_URL = 'common_redirect_after_login'
SOCIAL_AUTH_BACKEND_ERROR_URL = '/login/'
SOCIAL_AUTH_LOGIN_ERROR_URL = '/login/'

PHOTO_USER_DEFAULT = "logos_TRM/logo_TRM_user_default.png"
LOGO_CANDIDATE_DEFAULT = "logos_TRM/logo_TRM_user_default.png"
LOGO_COMPANY_DEFAULT = "logos_TRM/logo_TRM_company_default.png"

DEFAULT_SITE_TEMPLATE = 1
number_objects_page = 20
num_pages = 8

days_default_search = 30

INSTALLED_APPS = (
'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'django.contrib.humanize',
    'companies',
    'candidates',
    'rosetta',
    'common',
    'vacancies',
    'activities',
    'pytz',
    'weasyprint',
    'upload_logos',
    'ckeditor',
    'payments',
    'django_crontab',
    'django_extensions',
    'markdownify',
    'bootstrapform',
    # 'helpdesk',
    'django_comments',
    'mptt',
    'tagging',
    # 'zinnia',
    'el_pagination',
    'scheduler',
    'customField',
    'rest_framework',
)



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 'TRM.middleware.CrossDomainSessionMiddleware',
    #'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'TRM.middleware.SubdomainMiddleware',
    'TRM.middleware.ExpiredPlanMiddleware',
    'TRM.middleware.MediumMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_PATH, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'TRM.context_processors.project_name',
                'TRM.context_processors.user_profile',
                'TRM.context_processors.candidate_full_name',
                'TRM.context_processors.logo_candidate_default',
                'TRM.context_processors.logo_company_default',
                'TRM.context_processors.subdomain',
                'TRM.context_processors.notifications',
                'TRM.context_processors.packages',
            ],
        },
    },
]

CRONJOBS = [
    ('* * * * *', 'payments.cron.SubscriptionCronJob', f'>> {PROJECT_PATH}/cronjob.log'),
    ('0 0 * * *', 'vacancies.cron.PublishCronJob', f'>> {PROJECT_PATH}/cronjob.log'),
    ('0 0 * * *', 'vacancies.cron.UnPublishCronJob', f'>> {PROJECT_PATH}/cronjob.log'),
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_PIPELINE = (
    'common.views.save_candidate_social_data',
)

# OAuth configuration keys
SOCIAL_AUTH_KEYS = {
    'FACEBOOK_KEY': os.getenv('facebook_oauth_key'),
    'FACEBOOK_SECRET': os.getenv('facebook_oauth_secret'),
    'LINKEDIN_KEY': os.getenv('linkedin_oauth_key'),
    'LINKEDIN_SECRET': os.getenv('linkedin_oauth_secret'),
    'ANGEL_KEY': os.getenv('angel_oauth_key'),
    'ANGEL_SECRET': os.getenv('angel_oauth_secret'),
    'TWITTER_KEY': os.getenv('twitter_oauth_key'),
    'TWITTER_SECRET': os.getenv('twitter_oauth_secret'),
    'GOOGLEPLUS_KEY': os.getenv('googleplus_oauth_key'),
    'GOOGLEPLUS_SECRET': os.getenv('googleplus_oauth_secret'),
    'GITHUB_KEY': os.getenv('github_oauth_key'),
    'GITHUB_SECRET': os.getenv('github_oauth_secret'),
    'STACKOVERFLOW_KEY': os.getenv('stackoverflow_oauth_key'),
    'STACKOVERFLOW_SECRET': os.getenv('stackoverflow_oauth_secret'),
    'STACKOVERFLOW_REQUESTKEY': os.getenv('stackoverflow_oauth_requestkey'),
}

# PayPal SDK Setup
PAYPAL_CLIENT_ID = os.getenv('paypal_client_id')
PAYPAL_APP_SECRET = os.getenv('paypal_app_secret')
paypalrestsdk.configure({
    'mode': 'live' if ENVIRONMENT == 'productive' else 'sandbox',
    'client_id': PAYPAL_CLIENT_ID,
    'client_secret': PAYPAL_APP_SECRET,
})

# Email Settings
EMAIL_BACKEND = os.getenv('email_backend')
EMAIL_HOST = os.getenv('email_host')
EMAIL_PORT = os.getenv('email_port')
EMAIL_HOST_USER = os.getenv('email_host_user')
EMAIL_HOST_PASSWORD = os.getenv('email_host_passw')
EMAIL_USE_TLS = os.getenv('email_use_tls')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = os.getenv('server_email')

# Database Config
DATABASES = {
    'default': {
        'ENGINE': os.getenv('db_engine'),
        'NAME': os.getenv('db_name'),
        'USER': os.getenv('db_user'),
        'PASSWORD': os.getenv('db_password'),
        'HOST': os.getenv('db_host'),
        'PORT': os.getenv('db_port') or os.getenv('db_host'),
    }
}

# Media & Static Files
MEDIA_ROOT = os.getenv('media_root', os.path.join(PROJECT_PATH, 'media'))
MEDIA_URL = os.getenv('media_url', 'http://spotaxis.com/media/')
STATIC_ROOT = os.getenv('static_root', '')
STATICFILES_DIRS = [
    os.getenv('static_dir') or os.path.join(PROJECT_PATH, 'static')
]

# Site URL
PROTOCOL = 'https' if ENVIRONMENT == 'productive' else 'http'
SITE_URL = os.getenv('site_url', f"{PROTOCOL}://spotaxis.com")
SITE_SUFFIX = os.getenv('site_suffix', '.spotaxis.com/')

logo_email = os.getenv('logo_email')
NOTIFICATION_EMAILS = os.getenv('notification_emails')
CKEDITOR_UPLOAD_PATH = "uploads/"
X_FRAME_OPTIONS = 'SAMEORIGIN'