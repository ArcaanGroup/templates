"""Role domain entity"""
from datetime import datetime
from typing import List, Optional, Set
import uuid

from app.domain.entities.base import BaseEntity


class Role(BaseEntity):
    """Role domain entity with business logic"""

    def __init__(
        self,
        title: str,
        description: Optional[str] = None,
        permissions: Optional[List[uuid.UUID]] = None,
        id: Optional[uuid.UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        # Use uuid4 if no id is provided
        if id is None:
            id = uuid.uuid4()
        super().__init__(id, created_at, updated_at)
        self._title = title
        self._description = description
        self._permissions = permissions or []

    @property
    def title(self) -> str:
        """Role's title"""
        return self._title

    @property
    def description(self) -> Optional[str]:
        """Role's description"""
        return self._description

    @property
    def permissions(self) -> List[uuid.UUID]:
        """List of permission UUIDs associated with this role"""
        return self._permissions

    def update_title(self, new_title: str) -> None:
        """Update role's title"""
        self._title = new_title
        self.mark_as_updated()

    def update_description(self, new_description: str) -> None:
        """Update role's description"""
        self._description = new_description
        self.mark_as_updated()

    def add_permission(self, permission_id: uuid.UUID) -> None:
        """Add a permission to the role"""
        if permission_id not in self._permissions:
            self._permissions.append(permission_id)
            self.mark_as_updated()

    def remove_permission(self, permission_id: uuid.UUID) -> None:
        """Remove a permission from the role"""
        if permission_id in self._permissions:
            self._permissions.remove(permission_id)
            self.mark_as_updated()
