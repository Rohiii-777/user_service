class ServiceError(Exception):
    code: str
    message: str

    def __init__(self, message: str | None = None):
        if message:
            self.message = message
        super().__init__(self.message)


class UserAlreadyExists(ServiceError):
    code = "USER_ALREADY_EXISTS"
    message = "User already exists"


class InvalidCredentials(ServiceError):
    code = "INVALID_CREDENTIALS"
    message = "Invalid email or password"


class UserNotFound(ServiceError):
    code = "USER_NOT_FOUND"
    message = "User not found"


class InactiveUser(ServiceError):
    code = "USER_INACTIVE"
    message = "User account is inactive"
