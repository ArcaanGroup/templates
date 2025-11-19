"""Unit of Work pattern implementation"""
from abc import ABC, abstractmethod
from typing import AsyncContextManager

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.repositories import ItemRepositoryInterface
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.repositories.item_repository import SQLAlchemyItemRepository


class UnitOfWork(ABC):
    """Unit of Work interface"""
    
    items: ItemRepositoryInterface
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        await self.rollback()
    
    @abstractmethod
    async def commit(self) -> None:
        """Commit the transaction"""
        pass
    
    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the transaction"""
        pass


class SQLAlchemyUnitOfWork(UnitOfWork):
    """SQLAlchemy implementation of Unit of Work"""
    
    def __init__(self, session: AsyncSession | None = None):
        self._session = session or AsyncSessionLocal()
        self._items: ItemRepositoryInterface | None = None
    
    @property
    def items(self) -> ItemRepositoryInterface:
        """Get items repository"""
        if self._items is None:
            self._items = SQLAlchemyItemRepository(self._session)
        return self._items
    
    async def commit(self) -> None:
        """Commit the transaction"""
        await self._session.commit()
    
    async def rollback(self) -> None:
        """Rollback the transaction"""
        await self._session.rollback()
    
    async def __aexit__(self, *args):
        await self.rollback()
        await self._session.close()

