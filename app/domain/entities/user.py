"""User domain entity"""
from datetime import datetime
from typing import Optional

from app.domain.entities.base import BaseEntity
from app.domain.exceptions.auth_exceptions import (
    InvalidEmailException,
    InvalidPasswordException,
    InvalidUsernameException,
)
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.value_objects.username import Username


class User(BaseEntity):
    """User domain entity with business logic"""

    def __init__(
        self,
        username: Username,
        email: Email,
        password: Password,
        is_active: bool = True,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        super().__init__(id, created_at, updated_at)
        self._username = username
        self._email = email
        self._password = password
        self._is_active = is_active

    @property
    def username(self) -> Username:
        """User's username"""
        return self._username

    @property
    def email(self) -> Email:
        """User's email"""
        return self._email

    @property
    def password(self) -> Password:
        """User's password hash"""
        return self._password

    @property
    def is_active(self) -> bool:
        """Whether user account is active"""
        return self._is_active

    def update_username(self, new_username: Username) -> None:
        """Update user's username"""
        self._username = new_username
        self.mark_as_updated()

    def update_email(self, new_email: Email) -> None:
        """Update user's email"""
        self._email = new_email
        self.mark_as_updated()

    def update_password(self, new_password: Password) -> None:
        """Update user's password"""
        self._password = new_password
        self.mark_as_updated()

    def deactivate(self) -> None:
        """Deactivate user account"""
        self._is_active = False
        self.mark_as_updated()

    def activate(self) -> None:
        """Activate user account"""
        self._is_active = True
        self.mark_as_updated()

    def verify_password(self, plain_password: str) -> bool:
        """Verify if the provided password matches the stored password hash"""
        return self._password.verify(plain_password)
