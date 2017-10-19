from .base import *

DOMAIN = "LA_IP_EN_AMAZON_O_ALGO"
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
