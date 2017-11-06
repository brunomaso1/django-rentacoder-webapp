from .base import *

URL = "rent-a-coder.tk"
DOMAIN = "http://" + URL
IP = "34.212.201.181"
ALLOWED_HOSTS = [URL, IP]

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