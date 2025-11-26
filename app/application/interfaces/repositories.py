"""Repository interfaces"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional
import uuid

from app.domain.entities.user import User
from app.domain.entities.refresh_tokens.refresh_token import RefreshToken
from app.domain.entities.role import Role

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

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """List all users with pagination"""
        pass

    @abstractmethod
    async def count_all(self) -> int:
        """Count all users"""
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


class RoleRepositoryInterface(ABC):
    """Role repository interface"""

    @abstractmethod
    async def create(self, role: Role) -> Role:
        """Create a new role"""
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, role_id: uuid.UUID) -> Optional[Role]:
        """Get role by ID"""
        raise NotImplementedError

    @abstractmethod
    async def get_by_title(self, title: str) -> Optional[Role]:
        """Get role by title"""
        raise NotImplementedError

    @abstractmethod
    async def list_all(self) -> List[Role]:
        """List all roles"""
        raise NotImplementedError

    @abstractmethod
    async def update(self, role: Role) -> Role:
        """Update an existing role"""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, role_id: uuid.UUID) -> bool:
        """Delete a role by ID"""
        raise NotImplementedError

    @abstractmethod
    async def get_user_roles(self, user_id: int) -> List[Role]:
        """Get all roles for a specific user"""
        raise NotImplementedError
