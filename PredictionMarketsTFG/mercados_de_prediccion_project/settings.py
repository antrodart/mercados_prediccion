"""
Django settings for mercados_de_prediccion_project project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import django_heroku
from django.utils.translation import ugettext_lazy as _
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'hq@lu19)14%t^k=*4*rzod)*2gevj15w#!+eyf7xwaeefu*xo7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

if DEBUG == False:
	sentry_sdk.init(
	    dsn="https://0182ca349faa43a0a974cdb8b00bf92e@sentry.io/1461871",
	    integrations=[DjangoIntegration()]
	)

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mercados_de_prediccion',
    'users',
    'django_babel',
	'widget_tweaks',
	'social_django',
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'predictmarket.us@gmail.com'
EMAIL_HOST_PASSWORD = '$FC=us23AL8Y'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django_babel.middleware.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mercados_de_prediccion_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
				'django.template.context_processors.i18n',
				'social_django.context_processors.backends',
				'social_django.context_processors.login_redirect',
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = (
	'social_core.backends.open_id.OpenIdAuth',  #  for Google authentication
	'social_core.backends.google.GoogleOpenId',  #  for Google authentication
	'social_core.backends.google.GoogleOAuth2',  #  for Google authentication

	'django.contrib.auth.backends.ModelBackend',  #  default authentication
)

WSGI_APPLICATION = 'mercados_de_prediccion_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

if DEBUG:
	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.postgresql',
			'NAME': 'mercados_prediccion',
			'USER': 'postgres',
			'PASSWORD': '$FC=us23AL8Y',
			'HOST': 'localhost',
			'PORT': '5432',
		}
	}
else:
	if os.getenv('TRAVIS', None):
		DATABASES = {
			'default': {
				'ENGINE': 'django.db.backends.postgresql',
				'NAME': 'predictmarket',
				'USER': 'predictmarket',
				'PASSWORD': 'predictmarket',
				'HOST': 'localhost',
				'PORT': '5432',
			}
		}
	else:
		DATABASES = {
			'default': {
				'ENGINE': 'django.db.backends.postgresql',
				'NAME': 'd5rl33vg868tpb',
				'USER': 'gzaerkelumcqvo',
				'PASSWORD': 'c659aaa362c15ee59b23b3f1e7cb11aeab0d71f7500781af1663e056ed78555f',
				'HOST': 'ec2-54-227-245-146.compute-1.amazonaws.com',
				'PORT': '5432',
			}
		}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGES = (
	('en', _('English')),
	('es', _('Spanish'))
)
LANGUAGE_CODE = 'en'

LOCALE_PATHS = (
	os.path.join(BASE_DIR, 'mercados_de_prediccion\locale'),
)

TIME_ZONE = 'Europe/Madrid'

USE_I18N = True

USE_L10N = True

USE_TZ = True



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_URL = '/static/'
#PROJECT_DIR = os.path.dirname(__file__)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')



AUTH_USER_MODEL = 'users.User'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY ='33590752386-mk7r5mlu18n3gv29q2ulp59sd4dlgpjn.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'mYGYDr_D80enWb3GGaDHVDnK'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}

django_heroku.settings(locals())