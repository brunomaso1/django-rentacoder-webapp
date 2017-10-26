from .base import *

DOMAIN = "34.212.201.181"
ALLOWED_HOSTS = [DOMAIN]

#Hola soy un comentario

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'rentacoder',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
