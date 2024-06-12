class WrongUsernameOrPasswordError(Exception):
    pass


class UserNotActivatedError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass
