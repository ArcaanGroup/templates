"""Base entity class"""
from abc import ABC
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4


class BaseEntity(ABC):
    """Base class for all domain entities"""
    
    def __init__(self, id: int | None = None, created_at: datetime | None = None, updated_at: datetime | None = None):
        self._id = id
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()
    
    @property
    def id(self) -> int | None:
        """Entity identifier"""
        return self._id
    
    @property
    def created_at(self) -> datetime:
        """Creation timestamp"""
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        """Last update timestamp"""
        return self._updated_at
    
    def mark_as_updated(self) -> None:
        """Mark entity as updated"""
        self._updated_at = datetime.utcnow()
    
    def __eq__(self, other: Any) -> bool:
        """Equality comparison based on ID"""
        if not isinstance(other, BaseEntity):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Hash based on ID"""
        return hash(self.id) if self.id is not None else hash(id(self))

