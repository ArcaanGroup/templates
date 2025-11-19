"""Authentication domain exceptions"""

from app.domain.exceptions.base import DomainException


class UserNotFoundException(DomainException):
    """Raised when user is not found"""

    def __init__(self, identifier: str):
        super().__init__(f"User with identifier {identifier} not found", {"identifier": identifier})


class InvalidEmailException(DomainException):
    """Raised when email format is invalid"""

    def __init__(self, email: str):
        super().__init__(f"Invalid email format: {email}", {"email": email})


class InvalidUsernameException(DomainException):
    """Raised when username format is invalid"""

    def __init__(self, username: str):
        super().__init__(f"Invalid username format: {username}", {"username": username})


class InvalidPasswordException(DomainException):
    """Raised when password does not meet requirements"""

    def __init__(self, reason: str):
        super().__init__(f"Invalid password: {reason}")


class UserAlreadyExistsException(DomainException):
    """Raised when trying to create a user that already exists"""

    def __init__(self, identifier: str):
        super().__init__(
            f"User already exists with identifier: {identifier}", {"identifier": identifier}
        )


class AuthenticationFailedException(DomainException):
    """Raised when authentication fails"""

    def __init__(self, reason: str):
        super().__init__(f"Authentication failed: {reason}")


class InsufficientPermissionsException(DomainException):
    """Raised when user doesn't have required permissions"""

    def __init__(self):
        super().__init__("Insufficient permissions to perform this action")
