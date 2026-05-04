"""
User-related dependencies and dependency injection logic.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.user import (
    AssignRoleToUserUseCase,
    CreateUserUseCase,
    DeleteUserUseCase,
    GetAllUsersUseCase,
    GetUserByIdUseCase,
    RemoveRoleFromUserUseCase,
    UpdateUserUseCase,
)
from app.infra.core.database import get_db_session
from app.infra.repositories.role_repository import RoleRepository
from app.infra.repositories.user_repository import UserRepository
from app.interface.repository.role_repository_interface import IRoleRepository
from app.interface.repository.user_repository_interface import IUserRepository


async def get_user_repository(
    db_session: AsyncSession = Depends(get_db_session),
) -> IUserRepository:
    """Dependency to provide UserRepository instance with database session."""
    return UserRepository(db_session=db_session)


async def get_role_repository(
    db_session: AsyncSession = Depends(get_db_session),
) -> IRoleRepository:
    """Dependency to provide RoleRepository instance with database session."""
    return RoleRepository(db_session=db_session)


async def get_get_all_users_usecase(
    user_repository: IUserRepository = Depends(get_user_repository),
) -> GetAllUsersUseCase:
    """Dependency to provide GetAllUsersUseCase instance."""
    return GetAllUsersUseCase(user_repository)


async def get_get_user_by_id_usecase(
    user_repository: IUserRepository = Depends(get_user_repository),
) -> GetUserByIdUseCase:
    """Dependency to provide GetUserByIdUseCase instance."""
    return GetUserByIdUseCase(user_repository)


async def get_create_user_usecase(
    user_repository: IUserRepository = Depends(get_user_repository),
) -> CreateUserUseCase:
    """Dependency to provide CreateUserUseCase instance."""
    return CreateUserUseCase(user_repository)


async def get_update_user_usecase(
    user_repository: IUserRepository = Depends(get_user_repository),
) -> UpdateUserUseCase:
    """Dependency to provide UpdateUserUseCase instance."""
    return UpdateUserUseCase(user_repository)


async def get_delete_user_usecase(
    user_repository: IUserRepository = Depends(get_user_repository),
) -> DeleteUserUseCase:
    """Dependency to provide DeleteUserUseCase instance."""
    return DeleteUserUseCase(user_repository)


async def get_assign_role_to_user_usecase(
    user_repository: IUserRepository = Depends(get_user_repository),
    role_repository: IRoleRepository = Depends(get_role_repository),
) -> AssignRoleToUserUseCase:
    """Dependency to provide AssignRoleToUserUseCase instance."""
    return AssignRoleToUserUseCase(user_repository, role_repository)


async def get_remove_role_from_user_usecase(
    user_repository: IUserRepository = Depends(get_user_repository),
    role_repository: IRoleRepository = Depends(get_role_repository),
) -> RemoveRoleFromUserUseCase:
    """Dependency to provide RemoveRoleFromUserUseCase instance."""
    return RemoveRoleFromUserUseCase(user_repository, role_repository)
