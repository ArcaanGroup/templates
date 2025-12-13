"""
Permission service layer implementation.
"""

from typing import List

from app.interface.repositories.permission_repository_interface import (
    IPermissionRepository,
)
from app.models.permission.domain import PermissionDomain


class PermissionService:
    """Service class for permission-related business logic."""

    def __init__(self, permission_repository: IPermissionRepository):
        self.permission_repository = permission_repository

    async def get_all_permissions(self) -> List[PermissionDomain]:
        """Get all permissions."""
        return await self.permission_repository.get_all()

    async def get_permission_by_id(self, permission_id: str) -> PermissionDomain:
        """Get a permission by its ID."""
        permission = await self.permission_repository.get_by_id(permission_id)
        if permission is None:
            raise ValueError(f"Permission with ID {permission_id} not found")
        return permission

    async def get_permission_by_title(self, title: str) -> PermissionDomain:
        """Get a permission by its title."""
        permission = await self.permission_repository.get_by_title(title)
        if permission is None:
            raise ValueError(f"Permission with title {title} not found")
        return permission

    async def search_permissions_by_title(
        self, title_query: str
    ) -> List[PermissionDomain]:
        """Search permissions by title."""
        return await self.permission_repository.search_by_title(title_query)
