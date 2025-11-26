"""Domain exceptions"""

from .auth_exceptions import (
    AuthenticationFailedException,
    InsufficientPermissionsException,
    InvalidEmailException,
    InvalidPasswordException,
    InvalidUsernameException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from .general_exceptions import EntityNotFoundException

__all__ = [
    "AuthenticationFailedException",
    "InsufficientPermissionsException",
    "InvalidEmailException",
    "InvalidPasswordException",
    "InvalidUsernameException",
    "UserAlreadyExistsException",
    "UserNotFoundException",
    "EntityNotFoundException"
]
