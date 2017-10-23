from .base import *

DOMAIN = "34.212.201.181"
ALLOWED_HOSTS = [DOMAIN]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'rentacoder',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': 'LA_URL_EN_AMAZON_O_ALGO',
        'PORT': '5432',
    }
}
