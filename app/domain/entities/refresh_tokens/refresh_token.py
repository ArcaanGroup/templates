"""Refresh token domain entity"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from app.domain.entities.base import BaseEntity


class RefreshToken(BaseEntity):
    """Refresh token domain entity with business logic"""

    def __init__(
        self,
        token: str,
        user_id: int,
        expires_at: datetime,
        is_active: bool = True,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        super().__init__(id, created_at, updated_at)
        self._token = token
        self._user_id = user_id
        self._expires_at = expires_at
        self._is_active = is_active

    @property
    def token(self) -> str:
        """Refresh token value"""
        return self._token

    @property
    def user_id(self) -> int:
        """ID of the user associated with this refresh token"""
        return self._user_id

    @property
    def expires_at(self) -> datetime:
        """Expiration time of the refresh token"""
        return self._expires_at

    @property
    def is_active(self) -> bool:
        """Whether refresh token is active"""
        return self._is_active

    def deactivate(self) -> None:
        """Deactivate the refresh token"""
        self._is_active = False
        self.mark_as_updated()

    def is_expired(self) -> bool:
        """Check if the refresh token has expired"""
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Check if the refresh token is valid (active and not expired)"""
        return self.is_active and not self.is_expired()
