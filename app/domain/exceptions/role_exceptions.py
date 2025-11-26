"""Role-related domain exceptions"""

from app.domain.exceptions.base import DomainException


class RoleException(DomainException):
    """Base exception for role-related errors"""
    pass


class RoleNotFoundException(RoleException):
    """Raised when a role is not found"""
    pass


class RoleAlreadyExistsException(RoleException):
    """Raised when trying to create a role that already exists"""
    pass
