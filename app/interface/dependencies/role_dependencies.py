"""
Role-related dependencies and dependency injection logic.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.role import (
    AssignPermissionToRoleUseCase,
    CreateRoleUseCase,
    DeleteRoleUseCase,
    GetAllRolesUseCase,
    GetRoleByIdUseCase,
    RemovePermissionFromRoleUseCase,
    UpdateRoleUseCase,
)
from app.infra.core.database import get_db_session
from app.infra.repositories.permission_repository import JSONPermissionRepository
from app.infra.repositories.role_repository import RoleRepository
from app.interface.repository.permission_repository_interface import (
    IPermissionRepository,
)
from app.interface.repository.role_repository_interface import IRoleRepository


async def get_role_repository(
    db_session: AsyncSession = Depends(get_db_session),
) -> IRoleRepository:
    """Dependency to provide RoleRepository instance with database session."""
    return RoleRepository(db_session=db_session)


async def get_permission_repository() -> IPermissionRepository:
    """Dependency to provide PermissionRepository instance with database session."""
    return JSONPermissionRepository()


async def get_get_all_roles_usecase(
    role_repository: IRoleRepository = Depends(get_role_repository),
) -> GetAllRolesUseCase:
    """Dependency to provide GetAllRolesUseCase instance."""
    return GetAllRolesUseCase(role_repository)


async def get_get_role_by_id_usecase(
    role_repository: IRoleRepository = Depends(get_role_repository),
) -> GetRoleByIdUseCase:
    """Dependency to provide GetRoleByIdUseCase instance."""
    return GetRoleByIdUseCase(role_repository)


async def get_create_role_usecase(
    role_repository: IRoleRepository = Depends(get_role_repository),
    permission_repository: IPermissionRepository = Depends(get_permission_repository),
) -> CreateRoleUseCase:
    """Dependency to provide CreateRoleUseCase instance."""
    return CreateRoleUseCase(role_repository, permission_repository)


async def get_update_role_usecase(
    role_repository: IRoleRepository = Depends(get_role_repository),
    permission_repository: IPermissionRepository = Depends(get_permission_repository),
) -> UpdateRoleUseCase:
    """Dependency to provide UpdateRoleUseCase instance."""
    return UpdateRoleUseCase(role_repository, permission_repository)


async def get_delete_role_usecase(
    role_repository: IRoleRepository = Depends(get_role_repository),
) -> DeleteRoleUseCase:
    """Dependency to provide DeleteRoleUseCase instance."""
    return DeleteRoleUseCase(role_repository)


async def get_assign_permission_to_role_usecase(
    role_repository: IRoleRepository = Depends(get_role_repository),
    permission_repository: IPermissionRepository = Depends(get_permission_repository),
) -> AssignPermissionToRoleUseCase:
    """Dependency to provide AssignPermissionToRoleUseCase instance."""
    return AssignPermissionToRoleUseCase(role_repository, permission_repository)


async def get_remove_permission_from_role_usecase(
    role_repository: IRoleRepository = Depends(get_role_repository),
) -> RemovePermissionFromRoleUseCase:
    """Dependency to provide RemovePermissionFromRoleUseCase instance."""
    return RemovePermissionFromRoleUseCase(role_repository)
