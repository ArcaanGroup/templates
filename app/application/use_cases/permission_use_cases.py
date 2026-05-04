"""
True Clean Architecture Use Cases for Permission operations.
Use cases contain business logic and are independent of frameworks and external concerns.
"""

from dataclasses import dataclass
from typing import List, Optional

from app.domain.entities import PermissionEntity
from app.interface.repository.permission_repository_interface import (
    IPermissionRepository,
)


@dataclass(frozen=True)
class GetAllPermissionsRequest:
    """Input port for getting all permissions."""
    pass


@dataclass(frozen=True)
class GetAllPermissionsResponse:
    """Output port for getting all permissions."""
    permissions: List[PermissionEntity]


@dataclass(frozen=True)
class GetPermissionByIdRequest:
    """Input port for getting a permission by ID."""
    permission_id: str


@dataclass(frozen=True)
class GetPermissionByIdResponse:
    """Output port for getting a permission by ID."""
    permission: PermissionEntity


@dataclass(frozen=True)
class GetPermissionByTitleRequest:
    """Input port for getting a permission by title."""
    title: str


@dataclass(frozen=True)
class GetPermissionByTitleResponse:
    """Output port for getting a permission by title."""
    permission: PermissionEntity


@dataclass(frozen=True)
class SearchPermissionsRequest:
    """Input port for searching permissions by title."""
    title_query: str


@dataclass(frozen=True)
class SearchPermissionsResponse:
    """Output port for searching permissions by title."""
    permissions: List[PermissionEntity]


class GetAllPermissionsUseCase:
    """Use case for retrieving all permissions."""

    def __init__(self, permission_repository: IPermissionRepository):
        self._permission_repo = permission_repository

    async def execute(self, request: GetAllPermissionsRequest) -> GetAllPermissionsResponse:
        """Execute the use case to get all permissions."""
        permissions = await self._permission_repo.get_all()
        return GetAllPermissionsResponse(permissions=permissions)


class GetPermissionByIdUseCase:
    """Use case for retrieving a permission by ID."""

    def __init__(self, permission_repository: IPermissionRepository):
        self._permission_repo = permission_repository

    async def execute(
        self, request: GetPermissionByIdRequest
    ) -> GetPermissionByIdResponse:
        """Execute the use case to get a permission by ID."""
        permission = await self._permission_repo.get_by_id(request.permission_id)
        if permission is None:
            raise ValueError(f"Permission with ID {request.permission_id} not found")
        return GetPermissionByIdResponse(permission=permission)


class GetPermissionByTitleUseCase:
    """Use case for retrieving a permission by title."""

    def __init__(self, permission_repository: IPermissionRepository):
        self._permission_repo = permission_repository

    async def execute(
        self, request: GetPermissionByTitleRequest
    ) -> GetPermissionByTitleResponse:
        """Execute the use case to get a permission by title."""
        permission = await self._permission_repo.get_by_title(request.title)
        if permission is None:
            raise ValueError(f"Permission with title {request.title} not found")
        return GetPermissionByTitleResponse(permission=permission)


class SearchPermissionsUseCase:
    """Use case for searching permissions by title."""

    def __init__(self, permission_repository: IPermissionRepository):
        self._permission_repo = permission_repository

    async def execute(
        self, request: SearchPermissionsRequest
    ) -> SearchPermissionsResponse:
        """Execute the use case to search permissions by title."""
        permissions = await self._permission_repo.search_by_title(request.title_query)
        return SearchPermissionsResponse(permissions=permissions)
