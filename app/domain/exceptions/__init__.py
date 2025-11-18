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

__all__ = [
    "AuthenticationFailedException",
    "InsufficientPermissionsException",
    "InvalidEmailException",
    "InvalidPasswordException",
    "InvalidUsernameException",
    "UserAlreadyExistsException",
    "UserNotFoundException",
    "ItemNotFoundException",
    "InvalidItemPriceException",
    "ItemNameRequiredException",
]
