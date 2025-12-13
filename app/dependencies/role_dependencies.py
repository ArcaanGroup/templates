"""
role-related dependencies and dependency injection logic.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.dependencies.permission_dependencies import get_permission_service
from app.interface.repositories.role_repository_interface import IRoleRepository
from app.repository.role_repository import RoleRepository
from app.service.permission_service import PermissionService
from app.service.role_service import RoleService


async def get_role_repository(
    db_session: AsyncSession = Depends(get_db_session),
) -> IRoleRepository:
    """Dependency to provide RoleRepository instance with database session."""
    return RoleRepository(db_session=db_session)


async def get_role_service(
    role_repository: IRoleRepository = Depends(get_role_repository),
    permission_service: PermissionService = Depends(get_permission_service),
):
    """Dependency to provide RoleService instance with repository and permission service."""
    return RoleService(role_repository, permission_service)
