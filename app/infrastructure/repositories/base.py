"""Base repository implementation"""
from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

T = TypeVar("T")
M = TypeVar("M")  # Model type


class BaseRepository(Generic[T, M]):
    """Base repository with common operations"""
    
    def __init__(self, session: AsyncSession, model: type[M]):
        self.session = session
        self.model = model

