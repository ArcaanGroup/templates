"""Repository interfaces"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.domain.entities.item import Item

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

