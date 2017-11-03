from django.db import transaction
from rentacoder_app.models import EmailToken
import rentacoder_app.errors as err
from rentacoder_app.errors import Error


def verify_registration_token(token):
    error = ''
    verified = False

    try:
        with transaction.atomic():
            token_obj = EmailToken.objects.select_related('user').get(value=token)
            if token_obj.is_valid():
                token_obj.user.is_active = True
                token_obj.user.save()
                token_obj.delete()
                verified = True
            else:
                error = Error(err.ERROR_TOKEN_NOT_VALID)
    except EmailToken.DoesNotExist:
        error = Error(err.ERROR_TOKEN_NOT_FOUND)
    except Exception as e:
        error = Error(err.ERROR_UNKNOWN)

    return verified, error
