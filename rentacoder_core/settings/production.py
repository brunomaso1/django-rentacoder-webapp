from .base import *

DOMAIN = "54.187.175.219"
ALLOWED_HOSTS = [DOMAIN]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'rentacoder',
        'HOST': 'localhost',
        'PORT': '5432',
        'USER': 'djangodemo',
        'PASSWORD': 'djangodemo',
    }
}