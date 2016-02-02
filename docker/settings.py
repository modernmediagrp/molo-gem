"""Django settings for use within the docker container."""

from os import environ

import dj_database_url

from .base import *


# Disable debug mode

DEBUG = False
TEMPLATE_DEBUG = False

SECRET_KEY = environ.get('SECRET_KEY') or 'please-change-me'
PROJECT_ROOT = (
    environ.get('PROJECT_ROOT') or dirname(dirname(abspath(__file__))))

LANGUAGE_CODE = environ.get('LANGUAGE_CODE', 'en')

SERVICE_DIRECTORY_API_BASE_URL = environ.get(
    'SERVICE_DIRECTORY_API_BASE_URL', '')
SERVICE_DIRECTORY_API_USERNAME = environ.get(
    'SERVICE_DIRECTORY_API_USERNAME', '')
SERVICE_DIRECTORY_API_PASSWORD = environ.get(
    'SERVICE_DIRECTORY_API_PASSWORD', '')

GOOGLE_PLACES_API_SERVER_KEY = environ.get(
    'GOOGLE_PLACES_API_SERVER_KEY', '')

SERVICE_DIRECTORY_API_LOGIN = {
    'username': SERVICE_DIRECTORY_API_LOGIN_USERNAME,
    'password': SERVICE_DIRECTORY_API_LOGIN_PASSWORD}

RAVEN_DSN = environ.get('RAVEN_DSN')
RAVEN_CONFIG = {'dsn': RAVEN_DSN} if RAVEN_DSN else {}

COMPRESS_OFFLINE = True

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///%s' % (join(PROJECT_ROOT, 'gemmolo.db'),))}

MEDIA_ROOT = join(PROJECT_ROOT, 'media')

STATIC_ROOT = join(PROJECT_ROOT, 'static')

LOCALE_PATHS = (
    join(PROJECT_ROOT, "locale"),
)
