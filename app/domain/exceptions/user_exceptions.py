"""User-related domain exceptions"""

from app.domain.exceptions.base import DomainException


class UserException(DomainException):
    """Base exception for user-related errors"""
    pass


class UserNotFoundException(UserException):
    """Raised when a user is not found"""
    pass


class UserAlreadyExistsException(UserException):
    """Raised when trying to create a user that already exists"""
    pass
