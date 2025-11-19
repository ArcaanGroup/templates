"""Repository interfaces"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.domain.entities.item import Item
from app.domain.entities.user import User
from app.domain.entities.refresh_tokens.refresh_token import RefreshToken

T = TypeVar("T")


class RepositoryInterface(ABC, Generic[T]):
    """Base repository interface"""

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity"""
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> T | None:
        """Get entity by ID"""
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update an entity"""
        pass

    @abstractmethod
    async def delete(self, entity: T) -> None:
        """Delete an entity"""
        pass


class ItemRepositoryInterface(RepositoryInterface[Item], ABC):
    """Item repository interface"""

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Item]:
        """List all items with pagination"""
        pass


class UserRepositoryInterface(RepositoryInterface[User], ABC):
    """User repository interface"""

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        """Get user by username"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Get user by email"""
        pass

    @abstractmethod
    async def get_by_username_or_email(self, identifier: str) -> User | None:
        """Get user by username or email"""
        pass


class RefreshTokenRepositoryInterface(RepositoryInterface[RefreshToken], ABC):
    """Refresh token repository interface"""

    @abstractmethod
    async def get_by_token(self, token: str) -> RefreshToken | None:
        """Get refresh token by its value"""
        pass

    @abstractmethod
    async def get_active_by_user_id(self, user_id: int) -> list[RefreshToken]:
        """Get all active refresh tokens for a user"""
        pass

    @abstractmethod
    async def deactivate_by_token(self, token: str) -> None:
        """Deactivate a refresh token by its value"""
        pass

    @abstractmethod
    async def delete_expired_tokens(self) -> int:
        """Delete expired refresh tokens and return the number of deleted tokens"""
        pass
