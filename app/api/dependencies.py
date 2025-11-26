"""FastAPI dependencies"""

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.cache import CacheInterface
from app.application.interfaces.event_bus import EventBusInterface
from app.application.interfaces.repositories import UserRepositoryInterface, RoleRepositoryInterface
from app.application.use_cases.auth.change_password import ChangePasswordUseCase
from app.application.use_cases.auth.get_current_user import GetCurrentUserUseCase
from app.application.use_cases.auth.login import LoginUseCase
from app.application.use_cases.auth.register import RegisterUseCase
from app.application.use_cases.auth.refresh_token import RefreshTokenUseCase
from app.application.use_cases.auth.logout import LogoutUseCase
from app.application.use_cases.users.create_user import CreateUserUseCase
from app.application.use_cases.users.delete_user import DeleteUserUseCase
from app.application.use_cases.users.get_user import GetUserUseCase
from app.application.use_cases.users.list_users import ListUsersUseCase
from app.application.use_cases.users.update_user import UpdateUserUseCase
from app.application.use_cases.roles.create_role import CreateRoleUseCase
from app.application.use_cases.roles.delete_role import DeleteRoleUseCase
from app.application.use_cases.roles.get_role import GetRoleUseCase
from app.application.use_cases.roles.list_roles import ListRolesUseCase
from app.application.use_cases.roles.update_role import UpdateRoleUseCase
from app.application.use_cases.user_roles.assign_role_to_user import AssignRoleToUserUseCase
from app.application.use_cases.user_roles.get_user_roles import GetUserRolesUseCase
from app.application.dto.auth_dto import UserDTO
from app.core.security import oauth2_scheme, get_current_user
from app.infrastructure.cache.memory_cache import MemoryCache
from app.infrastructure.database.session import get_db
from app.infrastructure.messaging.event_bus import InMemoryEventBus
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from app.infrastructure.repositories.role_repository import SQLAlchemyRoleRepository
from app.infrastructure.repositories.refresh_token_repository import (
    SQLAlchemyRefreshTokenRepository,
)
from app.application.interfaces.repositories import RefreshTokenRepositoryInterface


# Cache singleton
_cache: CacheInterface | None = None


def get_cache() -> CacheInterface:
    """Get cache instance"""
    global _cache
    if _cache is None:
        _cache = MemoryCache()
    return _cache


# Event bus singleton
_event_bus: EventBusInterface | None = None


def get_event_bus() -> EventBusInterface:
    """Get event bus instance"""
    global _event_bus
    if _event_bus is None:
        _event_bus = InMemoryEventBus()
        # Register event handlers
        # Note: In a real app, this would be done at startup
    return _event_bus


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepositoryInterface:
    """Get user repository"""
    return SQLAlchemyUserRepository(db)


def get_refresh_token_repository(
    db: AsyncSession = Depends(get_db),
) -> RefreshTokenRepositoryInterface:
    """Get refresh token repository"""
    return SQLAlchemyRefreshTokenRepository(db)


def get_role_repository(db: AsyncSession = Depends(get_db)) -> RoleRepositoryInterface:
    """Get role repository"""
    return SQLAlchemyRoleRepository(db)




def get_create_user_use_case(
    repository: UserRepositoryInterface = Depends(get_user_repository),
    role_repository: RoleRepositoryInterface = Depends(get_role_repository),
    event_bus: EventBusInterface = Depends(get_event_bus),
) -> CreateUserUseCase:
    """Get create user use case"""
    return CreateUserUseCase(repository, role_repository, event_bus)


def get_get_user_use_case(
    repository: UserRepositoryInterface = Depends(get_user_repository),
    cache: CacheInterface = Depends(get_cache),
) -> GetUserUseCase:
    """Get get user use case"""
    return GetUserUseCase(repository, cache)


def get_list_users_use_case(
    repository: UserRepositoryInterface = Depends(get_user_repository),
) -> ListUsersUseCase:
    """Get list users use case"""
    return ListUsersUseCase(repository)


def get_update_user_use_case(
    repository: UserRepositoryInterface = Depends(get_user_repository),
    role_repository: RoleRepositoryInterface = Depends(get_role_repository),
    cache: CacheInterface = Depends(get_cache),
) -> UpdateUserUseCase:
    """Get update user use case"""
    return UpdateUserUseCase(repository, role_repository, cache)


def get_delete_user_use_case(
    repository: UserRepositoryInterface = Depends(get_user_repository),
    cache: CacheInterface = Depends(get_cache),
) -> DeleteUserUseCase:
    """Get delete user use case"""
    return DeleteUserUseCase(repository, cache)


def get_login_use_case(
    user_repository: UserRepositoryInterface = Depends(get_user_repository),
    refresh_token_repository: RefreshTokenRepositoryInterface = Depends(
        get_refresh_token_repository
    ),
) -> LoginUseCase:
    """Get login use case"""
    return LoginUseCase(
        user_repository=user_repository, refresh_token_repository=refresh_token_repository
    )


def get_register_use_case(
    user_repository: UserRepositoryInterface = Depends(get_user_repository),
    refresh_token_repository: RefreshTokenRepositoryInterface = Depends(
        get_refresh_token_repository
    ),
) -> RegisterUseCase:
    """Get register use case"""
    return RegisterUseCase(
        user_repository=user_repository, refresh_token_repository=refresh_token_repository
    )


def get_current_user_use_case(
    user_repository: UserRepositoryInterface = Depends(get_user_repository),
) -> GetCurrentUserUseCase:
    """Get get current user use case"""
    return GetCurrentUserUseCase(user_repository)


def get_change_password_use_case(
    user_repository: UserRepositoryInterface = Depends(get_user_repository),
) -> ChangePasswordUseCase:
    """Get change password use case"""
    return ChangePasswordUseCase(user_repository)


def get_refresh_token_use_case(
    refresh_token_repository: RefreshTokenRepositoryInterface = Depends(
        get_refresh_token_repository
    ),
    user_repository: UserRepositoryInterface = Depends(get_user_repository),
) -> RefreshTokenUseCase:
    """Get refresh token use case"""
    from app.core.config import settings

    return RefreshTokenUseCase(
        refresh_token_repository=refresh_token_repository,
        user_repository=user_repository,
        access_token_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )


def get_logout_use_case(
    refresh_token_repository: RefreshTokenRepositoryInterface = Depends(
        get_refresh_token_repository
    ),
) -> LogoutUseCase:
    """Get logout use case"""
    return LogoutUseCase(refresh_token_repository=refresh_token_repository)


def get_create_role_use_case(
    role_repository: RoleRepositoryInterface = Depends(get_role_repository),
    event_bus: EventBusInterface = Depends(get_event_bus),
) -> CreateRoleUseCase:
    """Get create role use case"""
    return CreateRoleUseCase(role_repository, event_bus)


def get_get_role_use_case(
    role_repository: RoleRepositoryInterface = Depends(get_role_repository),
) -> GetRoleUseCase:
    """Get get role use case"""
    return GetRoleUseCase(role_repository)


def get_list_roles_use_case(
    role_repository: RoleRepositoryInterface = Depends(get_role_repository),
) -> ListRolesUseCase:
    """Get list roles use case"""
    return ListRolesUseCase(role_repository)


def get_update_role_use_case(
    role_repository: RoleRepositoryInterface = Depends(get_role_repository),
) -> UpdateRoleUseCase:
    """Get update role use case"""
    return UpdateRoleUseCase(role_repository)


def get_delete_role_use_case(
    role_repository: RoleRepositoryInterface = Depends(get_role_repository),
) -> DeleteRoleUseCase:
    """Get delete role use case"""
    return DeleteRoleUseCase(role_repository)


async def get_current_user_from_token(
    token: str = Depends(oauth2_scheme),
    use_case: GetCurrentUserUseCase = Depends(get_current_user_use_case),
) -> UserDTO:
    """Get current user DTO from token"""
    return await use_case.execute(token)


# Authorization dependencies
from typing import List
import uuid

from fastapi import Depends, HTTPException, status

from app.application.interfaces.repositories import UserRepositoryInterface, RoleRepositoryInterface
from app.application.dto.auth_dto import UserDTO
from app.domain.services.permission_service import PermissionService


async def authorize_user(
    required_permissions: List[uuid.UUID] = None,
    user_repository: UserRepositoryInterface = Depends(get_user_repository),
    role_repository: RoleRepositoryInterface = Depends(get_role_repository)
):
    """
    Authorization dependency that extends the current authentication
    Checks if the authenticated user has the required permissions
    """
    if required_permissions is None:
        required_permissions = []

    async def authorization_dependency(
        current_user: UserDTO = Depends(get_current_user_from_token)
    ) -> UserDTO:
        # If no permissions are required, just return the authenticated user
        if not required_permissions:
            return current_user

        # Get user's roles and their permissions
        user_roles = await role_repository.get_user_roles(current_user.id)
        user_permissions = set()

        # Collect all permissions from user's roles
        for role in user_roles:
            user_permissions.update(role.permissions)

        # Check if user has all required permissions
        for required_permission in required_permissions:
            if required_permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User does not have required permissions"
                )

        return current_user

    return authorization_dependency


# User Role dependencies
def get_assign_role_to_user_use_case(
    user_repository: UserRepositoryInterface = Depends(get_user_repository),
    role_repository: RoleRepositoryInterface = Depends(get_role_repository),
) -> AssignRoleToUserUseCase:
    """Get assign role to user use case"""
    return AssignRoleToUserUseCase(user_repository, role_repository)


def get_get_user_roles_use_case(
    user_repository: UserRepositoryInterface = Depends(get_user_repository),
) -> GetUserRolesUseCase:
    """Get get user roles use case"""
    return GetUserRolesUseCase(user_repository)
