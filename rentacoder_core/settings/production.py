from .base import *

DOMAIN = "http://rent-a-coder.tk"
IP = "34.212.201.181"
ALLOWED_HOSTS = [DOMAIN, IP]

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