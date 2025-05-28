# -*- coding: utf-8 -*-

# Django settings for TRM project.

from __future__ import absolute_import
import os.path
from rest_framework.permissions import AllowAny

PROJECT_NAME = 'SpotAxis'

PROJECT_PATH = os.path.dirname(os.path.realpath(__file__))

ADMINS = (('Saket', 'saket@spotaxis.com'),('Holesh','holesh@spotaxis.com'))

MANAGERS = ADMINS

ALLOWED_HOSTS = ['*']

# SESSION_COOKIE_DOMAIN = '.'

# SESSION_COOKIE_NAME = 'sessionid'

# En ENVIROMENT se establece en que ambiente se esta trabajando, hay 3 ambientes
    # local_development: Desarrollo en la propia maquina
    # server_development: Desarrollo y pruebas en el servidor antes de pasar en productivo
    # productive: Ambiente totalmente en productivo

from environment import ENVIRONMENT

if ENVIRONMENT == 'local_development' or ENVIRONMENT == 'server_development':
    NOTIFICATION_EMAILS = ['notify@spotaxis.com']
    DEBUG = True
else:
    NOTIFICATION_EMAILS = ['notify@spotaxis.com']
    DEBUG = False

# Dependiendo el ambiente se importan diferentes configuraciones
if ENVIRONMENT == 'local_development':
    from .settings_local_development import *
    HOSTED_URL = "http://spotaxis.com"
    ROOT_DOMAIN = "spotaxis"
elif ENVIRONMENT == 'server_development':
    HOSTED_URL = "http://demo.spotaxis.com"
    ROOT_DOMAIN = "demo.spotaxis"
    from .settings_server_development import *
elif ENVIRONMENT == 'productive':
    HOSTED_URL = "https://spotaxis.com"
    from .settings_productive import *
    ROOT_DOMAIN = "spotaxis"

TIME_ZONE = 'Asia/Kolkata'

LANGUAGE_CODE = 'en-IN'

gettext = lambda s: s

LANGUAGES = (
    ('en', gettext('English')),
)

SITE_ID = 1

USE_I18N = True

DEFAULT_SITE_TEMPLATE = 1

# If you set this to False, Django will not format dates, numbers and calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

STATIC_URL = '/static/'

# List of finder classes that know how to find static files in various locations.
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
]

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'o&amp;-l=w!!q%mgfn9#%9wdawrifyy+bsxr38b$p4ujw%ok=zv9&amp;d'

# Change the defautl Serialization in Django 1.6 form Json to Pickle
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

ROOT_URLCONF = 'TRM.urls'

SUBDOMAIN_URLCONF = 'TRM.subdomain_urls'

SUPPORT_URLCONF = 'TRM.support_urls'

BLOG_URLCONF = 'TRM.blog_urls'

DJANGO_SETTINGS_MODULE = 'TRM.settings'

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

AUTH_USER_MODEL = 'common.User'

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    # 'TRM.middleware.CrossDomainSessionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'TRM.middleware.SessionHostDomainMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'TRM.middleware.CustomSocialAuthExceptionMiddleware',
    'TRM.middleware.SubdomainMiddleware',
    'TRM.middleware.ExpiredPlanMiddleware',
    'TRM.middleware.MediumMiddleware',
]
CRONJOBS = [
    # ('*/5 * * * *', 'helpdesk.cron.EmailTicketCronJob', '>> '+PROJECT_PATH+'cronjob.log'),
    ('* * * * *', 'payments.cron.SubscriptionCronJob', '>> '+PROJECT_PATH+'cronjob.log'),
    ('0 0 * * *', 'vacancies.cron.PublishCronJob', '>> '+PROJECT_PATH+'cronjob.log'),
    ('0 0 * * *', 'vacancies.cron.UnPublishCronJob', '>> '+PROJECT_PATH+'cronjob.log'),
    # ...
]
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_PATH, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.core.context_processors.debug',
                'django.core.context_processors.i18n',
                'django.core.context_processors.media',
                'django.core.context_processors.static',
                'django.core.context_processors.request',
                'django.core.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'TRM.context_processors.project_name',
                'TRM.context_processors.user_profile',
                'TRM.context_processors.candidate_full_name',
                'TRM.context_processors.logo_candidate_default',
                'TRM.context_processors.logo_company_default',
                'TRM.context_processors.subdomain',
                'TRM.context_processors.notifications',
                'TRM.context_processors.packages',
                # 'social.apps.django_app.context_processors.backends',
                # 'social.apps.django_app.context_processors.login_redirect',
                # 'zinnia.context_processors.version',
            ],
        },
    },
]

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'TRM.wsgi.application'

CKEDITOR_UPLOAD_PATH = "uploads/"

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'helpdesk': {
            'level': 'DEBUG',
            'filters': [],
            'class': 'logging.FileHandler',
            'filename': PROJECT_PATH+'/debug.log'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django_crontab.crontab': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        # 'helpdesk': {
        #     'handlers': ['helpdesk', 'mail_admins'],
        #     'level': 'DEBUG',
        #     'propagate': True
        # },
        'werkzeug': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
SESSION_COOKIE_DOMAIN = '.spotaxis.com'

days_default_search = 30

AUTHENTICATION_BACKENDS = (
    # 'social.backends.facebook.FacebookOAuth2',
    # 'social.backends.open_id.OpenIdAuth',
    # 'social.backends.google.GoogleOpenId',
    # 'social.backends.google.GoogleOAuth2',
    # 'social.backends.google.GoogleOAuth',
    # 'social.backends.twitter.TwitterOAuth',
    # 'social.backends.yahoo.YahooOpenId',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_PIPELINE = (
    # 'social.pipeline.social_auth.social_details',
    # 'social.pipeline.social_auth.social_uid',
    # 'social.pipeline.social_auth.auth_allowed',
    # 'social.pipeline.social_auth.social_user',
    # 'social.pipeline.user.get_username',
    # 'social.pipeline.user.create_user',
    # 'social.pipeline.social_auth.associate_user',
    # 'social.pipeline.social_auth.load_extra_data',
    # 'social.pipeline.user.user_details',
    'common.views.save_candidate_social_data',
)

# Para el correcto funcionamiento al momento de loguearse
LOGIN_URL = '/login/'  # @login_required
LOGIN_ERROR_URL = '/login/'
LOGIN_REDIRECT_URL = 'common_redirect_after_login'

SOCIAL_AUTH_BACKEND_ERROR_URL = '/login/'
SOCIAL_AUTH_LOGIN_ERROR_URL = '/login/'

# Pide a facebook la dirección de email
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']

# Datos de conexión con la App de Google
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '685803913612-84edpb92a8e48ir84s1adgbs3opmvrb1.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '5NP3l5qlQ81LCIpA6SLeLk__'

# Logos por default para cuando empresas y candidatos no tienen una foto o logo en el sistema
# o bien para cuando se muestran vacantes confidenciales
PHOTO_USER_DEFAULT = "logos_TRM/logo_TRM_user_default.png"
LOGO_CANDIDATE_DEFAULT = "logos_TRM/logo_TRM_user_default.png"
LOGO_COMPANY_DEFAULT = "logos_TRM/logo_TRM_company_default.png"

# SOCIALMULTISHARE_TWITTER_OAUTH_KEY = "7Y2xar0P1UPdolrt3XmKawlMh"
# SOCIALMULTISHARE_TWITTER_OAUTH_SECRET = "Mhdx5JEYN73htm0PnNDtgbsGZvgy03fMghFATzyfrcx6NpCqhB"

# if ENVIRONMENT == 'productive':
#     pass
#     SOCIALMULTISHARE_FACEBOOK_OAUTH_KEY = "886020148168119"
#     SOCIALMULTISHARE_FACEBOOK_OAUTH_SECRET = "b7e32633ce8789a7ff072971cf12e303"
# else:
#     SOCIALMULTISHARE_FACEBOOK_OAUTH_KEY = "886020148168119"
#     SOCIALMULTISHARE_FACEBOOK_OAUTH_SECRET = "b7e32633ce8789a7ff072971cf12e303"

# SOCIALMULTISHARE_LINKEDIN_OAUTH_KEY = '75tlwz3vtjnw5w'
# SOCIALMULTISHARE_LINKEDIN_OAUTH_SECRET = '7v29PqVN6IlOTZr7'

# Variables para paginación
# Número de páginas visibles antes y después de los puntos de división
num_pages=8
# Número de objetos por página
number_objects_page=20

social_application_list = ['fb', 'li', 'gp', 'an', 'gh', 'so', 'tw']

REST_FRAMEWORK = {
    # 'DEFAULT_AUTHENTICATION_CLASSES': (
    #     Add an authentication method for the APIs
    # ),
    'DEFAULT_PERMISSION_CLASSES': [
        #using 'allow any' permission class until authentication is needed and/ an authentication method is agreed upon.
        #change permission class once required.
        'rest_framework.permissions.AllowAny'
        #'rest_framework.permissions.IsAuthenticated',
    ],
}