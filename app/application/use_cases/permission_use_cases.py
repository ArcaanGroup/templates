from typing import List

from app.domain.entities import PermissionEntity
from app.interface.repository.permission_repository_interface import (
    IPermissionRepository,
)


class PermissionUseCase:
    """Use case layer for permission operations."""

    def __init__(self, permission_repository: IPermissionRepository):
        self.permission_repository = permission_repository

    async def get_all_permissions(self) -> List[PermissionEntity]:
        return await self.permission_repository.get_all()

    async def get_permission_by_id(self, permission_id: str) -> PermissionEntity:
        permission = await self.permission_repository.get_by_id(permission_id)
        if permission is None:
            raise ValueError(f"Permission with ID {permission_id} not found")
        return permission

    async def get_permission_by_title(self, title: str) -> PermissionEntity:
        permission = await self.permission_repository.get_by_title(title)
        if permission is None:
            raise ValueError(f"Permission with title {title} not found")
        return permission

    async def search_permissions_by_title(
        self, title_query: str
    ) -> List[PermissionEntity]:
        return await self.permission_repository.search_by_title(title_query)
