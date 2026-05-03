"""
Permission-related dependencies and dependency injection logic.
"""

from fastapi import Depends

from app.application.use_cases.permission_use_cases import PermissionUseCase
from app.infrastructure.repository.permission_repository import JSONPermissionRepository
from app.interface.repositories.permission_repository_interface import (
    IPermissionRepository,
)


async def get_permission_repository() -> IPermissionRepository:
    """Dependency to provide JSONPermissionRepository instance."""
    return JSONPermissionRepository()


async def get_permission_service(
    permission_repository: IPermissionRepository = Depends(get_permission_repository),
) -> PermissionUseCase:
    """Dependency to provide PermissionUseCase instance."""
    return PermissionUseCase(permission_repository)
