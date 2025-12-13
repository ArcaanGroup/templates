"""
Interface for role repository operations.
This follows the dependency inversion principle by having the service layer
depend on this abstraction rather than concrete implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional

from fastapi_pagination import Page, Params

from app.models.role.domain import RoleDomain


class IRoleRepository(ABC):
    """Interface for role repository operations."""

    @abstractmethod
    async def get_all(self, params: Params) -> Page[RoleDomain]:
        """Get all roles from the repository."""
        pass

    @abstractmethod
    async def get_by_id(self, role_id: str) -> Optional[RoleDomain]:
        """Get a role by ID from the repository."""
        pass

    @abstractmethod
    async def create(self, created_domain: RoleDomain) -> RoleDomain:
        """Create a new role in the repository."""
        pass

    @abstractmethod
    async def update(self, updated_domain: RoleDomain) -> Optional[RoleDomain]:
        """Update a role in the repository."""
        pass

    @abstractmethod
    async def delete(self, role_id: str) -> Optional[RoleDomain]:
        """Delete a role from the repository."""
        pass
