from django.utils import timezone
import rentacoder_app.constants as const


def default_expiration_delta():
    """
    Generates the default expiration delta
    :return: Default time delta
    """
    return timezone.now() + const.EXPIRY_TOKEN_DELTA
