class InvalidUserCodeError(Exception):
    pass


class ExpiredUserCodeError(Exception):
    pass


class UserCodeNotFoundError(InvalidUserCodeError):
    pass


class UserCodeAvailabilityNeverStartedError(InvalidUserCodeError):
    pass


class UserAlreadyActivatedError(Exception):
    pass


class RetryableMailError(Exception):
    pass
