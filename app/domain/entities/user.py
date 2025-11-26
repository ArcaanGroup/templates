"""User domain entity"""
from datetime import datetime
from typing import Optional, List

from app.domain.entities.base import BaseEntity
from app.domain.entities.role import Role
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
        roles: Optional[List[Role]] = None,
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
        self._roles = roles or []

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

    @property
    def roles(self) -> List[Role]:
        """User's roles"""
        return self._roles

    def add_role(self, role: Role) -> None:
        """Add a role to the user"""
        if role not in self._roles:
            self._roles.append(role)
            self.mark_as_updated()

    def remove_role(self, role: Role) -> None:
        """Remove a role from the user"""
        if role in self._roles:
            self._roles.remove(role)
            self.mark_as_updated()

    def has_role(self, role_title: str) -> bool:
        """Check if user has a specific role by title"""
        return any(role.title.value == role_title for role in self._roles)

    def has_any_role(self, role_titles: List[str]) -> bool:
        """Check if user has any of the specified roles"""
        user_role_titles = [role.title.value for role in self._roles]
        return bool(set(role_titles) & set(user_role_titles))

    def has_all_roles(self, role_titles: List[str]) -> bool:
        """Check if user has all of the specified roles"""
        user_role_titles = [role.title.value for role in self._roles]
        return all(title in user_role_titles for title in role_titles)

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

    def update_roles(self, roles: List[Role]) -> None:
        """Update user's roles"""
        self._roles = roles
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
