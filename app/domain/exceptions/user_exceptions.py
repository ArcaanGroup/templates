"""User-related domain exceptions"""

from app.domain.exceptions.base import DomainException


class UserException(DomainException):
    """Base exception for user-related errors"""
    pass


class UserNotFoundException(UserException):
    """Raised when a user is not found"""

    def __init__(self, message: str = "User not found"):
        super().__init__(message)


class UserAlreadyExistsException(UserException):
    """Raised when trying to create a user that already exists"""

    def __init__(self, message: str = "User already exists"):
        super().__init__(message)
