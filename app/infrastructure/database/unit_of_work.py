"""Unit of Work pattern implementation"""
from abc import ABC, abstractmethod
from typing import AsyncContextManager

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import AsyncSessionLocal


class UnitOfWork(ABC):
    """Unit of Work interface"""

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

    async def commit(self) -> None:
        """Commit the transaction"""
        await self._session.commit()

    async def rollback(self) -> None:
        """Rollback the transaction"""
        await self._session.rollback()

    async def __aexit__(self, *args):
        await self.rollback()
        await self._session.close()
