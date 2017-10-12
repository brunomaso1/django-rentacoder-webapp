# errors definition
ERROR_PREFIX = 'E0x0'
ERROR_UNKNOWN = ERROR_PREFIX + '0'
ERROR_USERNAME_IN_USE = ERROR_PREFIX + '1'
ERROR_EMAIL_IN_USE = ERROR_PREFIX + '2'
ERROR_TOKEN_NOT_FOUND = ERROR_PREFIX + '3'
ERROR_TOKEN_NOT_VALID = ERROR_PREFIX + '4'
ERROR_RESET_PASSWORD_EXPIRED = ERROR_PREFIX + '5'
ERROR_RESET_PASSWORD_NOT_MATCH = ERROR_PREFIX + '6'
ERROR_INVALID_PASSWORD = ERROR_PREFIX + '7'

# errors text
ERRORS = {
    ERROR_UNKNOWN: 'Unknown error.',
    ERROR_USERNAME_IN_USE: 'Username already in use.',
    ERROR_EMAIL_IN_USE: 'Email already in use.',
    ERROR_TOKEN_NOT_FOUND: 'Token does not exist.',
    ERROR_TOKEN_NOT_VALID: 'Invalid token.',
    ERROR_RESET_PASSWORD_EXPIRED: 'Your token has expired, please request the password reset again.'
}


class Error:
    """
    Class used to represent an error
    """
    code = ERROR_UNKNOWN
    text = ERRORS.get(ERROR_UNKNOWN)

    def __init__(self, code):
        """
        Retrieves error text given error code
        :param code: The error code
        """
        self.code = code
        self.text = ERRORS.get(code, ERROR_UNKNOWN)
