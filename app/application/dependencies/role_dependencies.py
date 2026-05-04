"""
role-related dependencies and dependency injection logic.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dependencies.permission_dependencies import (
    get_permission_repository,
)
from app.application.use_cases.role_use_cases import RoleUseCase
from app.infrastructure.core.database import get_db_session
from app.infrastructure.repositories.role_repository import RoleRepository
from app.interface.repository.permission_repository_interface import (
    IPermissionRepository,
)
from app.interface.repository.role_repository_interface import IRoleRepository


async def get_role_repository(
    db_session: AsyncSession = Depends(get_db_session),
) -> IRoleRepository:
    """Dependency to provide RoleRepository instance with database session."""
    return RoleRepository(db_session=db_session)


async def get_role_service(
    role_repository: IRoleRepository = Depends(get_role_repository),
    permission_repository: IPermissionRepository = Depends(get_permission_repository),
) -> RoleUseCase:
    """Dependency to provide RoleUseCase instance with repository and permission adapter."""
    return RoleUseCase(role_repository, permission_repository)
