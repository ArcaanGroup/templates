"""FastAPI dependencies"""

from typing import AsyncGenerator

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.auth_dto import UserDTO
from app.application.interfaces.cache import CacheInterface
from app.application.interfaces.event_bus import EventBusInterface
from app.application.interfaces.repositories import (
    RefreshTokenRepositoryInterface,
    RoleRepositoryInterface,
    UserRepositoryInterface,
)
from app.core.security import get_current_user, oauth2_scheme
from app.infrastructure.cache.memory_cache import MemoryCache
from app.infrastructure.database.session import get_db
from app.infrastructure.messaging.event_bus import InMemoryEventBus
from app.infrastructure.repositories.refresh_token_repository import (
    SQLAlchemyRefreshTokenRepository,
)
from app.infrastructure.repositories.role_repository import SQLAlchemyRoleRepository
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from app.services.auth_service import AuthService
from app.services.role_service import RoleService
from app.services.user_service import UserService

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


def get_user_service(
    user_repository: UserRepositoryInterface = Depends(get_user_repository),
    role_repository: RoleRepositoryInterface = Depends(get_role_repository),
    refresh_token_repository: RefreshTokenRepositoryInterface = Depends(
        get_refresh_token_repository
    ),
) -> UserService:
    """Get user service"""
    return UserService(user_repository, role_repository, refresh_token_repository)


def get_role_service(
    role_repository: RoleRepositoryInterface = Depends(get_role_repository),
) -> RoleService:
    """Get role service"""
    return RoleService(role_repository)


def get_auth_service(
    user_repository: UserRepositoryInterface = Depends(get_user_repository),
    refresh_token_repository: RefreshTokenRepositoryInterface = Depends(
        get_refresh_token_repository
    ),
) -> AuthService:
    """Get auth service"""
    return AuthService(user_repository, refresh_token_repository)


def get_login_use_case(
    user_repository: UserRepositoryInterface = Depends(get_user_repository),
    refresh_token_repository: RefreshTokenRepositoryInterface = Depends(
        get_refresh_token_repository
    ),
) -> "LoginUseCase":
    """Get login use case"""
    from app.application.use_cases.auth.login import LoginUseCase

    return LoginUseCase(user_repository, refresh_token_repository)


def get_register_use_case(
    user_repository: UserRepositoryInterface = Depends(get_user_repository),
    refresh_token_repository: RefreshTokenRepositoryInterface = Depends(
        get_refresh_token_repository
    ),
) -> "RegisterUseCase":
    """Get register use case"""
    from app.application.use_cases.auth.register import RegisterUseCase

    return RegisterUseCase(user_repository, refresh_token_repository)


def get_change_password_use_case(
    user_repository: UserRepositoryInterface = Depends(get_user_repository),
) -> "ChangePasswordUseCase":
    """Get change password use case"""
    from app.application.use_cases.auth.change_password import ChangePasswordUseCase

    return ChangePasswordUseCase(user_repository)


def get_current_user_use_case(
    user_repository: UserRepositoryInterface = Depends(get_user_repository),
) -> "GetCurrentUserUseCase":
    """Get current user use case"""
    from app.application.use_cases.auth.get_current_user import GetCurrentUserUseCase

    return GetCurrentUserUseCase(user_repository)


def get_refresh_token_use_case(
    refresh_token_repository: RefreshTokenRepositoryInterface = Depends(
        get_refresh_token_repository
    ),
    user_repository: UserRepositoryInterface = Depends(get_user_repository),
) -> "RefreshTokenUseCase":
    """Get refresh token use case"""
    from app.application.use_cases.auth.refresh_token import RefreshTokenUseCase

    return RefreshTokenUseCase(refresh_token_repository, user_repository)


def get_logout_use_case(
    refresh_token_repository: RefreshTokenRepositoryInterface = Depends(
        get_refresh_token_repository
    ),
) -> "LogoutUseCase":
    """Get logout use case"""
    from app.application.use_cases.auth.logout import LogoutUseCase

    return LogoutUseCase(refresh_token_repository)


def get_create_role_use_case(
    role_repository: RoleRepositoryInterface = Depends(get_role_repository),
    user_repository: UserRepositoryInterface = Depends(get_user_repository),
) -> "CreateRoleUseCase":
    """Get create role use case"""
    from app.application.use_cases.roles.create_role import CreateRoleUseCase

    return CreateRoleUseCase(role_repository, user_repository)


def get_get_role_use_case(
    role_repository: RoleRepositoryInterface = Depends(get_role_repository),
) -> "GetRoleUseCase":
    """Get get role use case"""
    from app.application.use_cases.roles.get_role import GetRoleUseCase

    return GetRoleUseCase(role_repository)


def get_list_roles_use_case(
    role_repository: RoleRepositoryInterface = Depends(get_role_repository),
) -> "ListRolesUseCase":
    """Get list roles use case"""
    from app.application.use_cases.roles.list_roles import ListRolesUseCase

    return ListRolesUseCase(role_repository)


def get_update_role_use_case(
    role_repository: RoleRepositoryInterface = Depends(get_role_repository),
    user_repository: UserRepositoryInterface = Depends(get_user_repository),
) -> "UpdateRoleUseCase":
    """Get update role use case"""
    from app.application.use_cases.roles.update_role import UpdateRoleUseCase

    return UpdateRoleUseCase(role_repository, user_repository)


def get_delete_role_use_case(
    role_repository: RoleRepositoryInterface = Depends(get_role_repository),
) -> "DeleteRoleUseCase":
    """Get delete role use case"""
    from app.application.use_cases.roles.delete_role import DeleteRoleUseCase

    return DeleteRoleUseCase(role_repository)


async def get_current_user_from_token(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
) -> UserDTO:
    """Get current user DTO from token"""
    from app.core.security import get_current_user as get_user_from_token

    # Get user data from the token
    user_data = await get_user_from_token(token)

    # Get user by username or email from the repository
    user_model = await user_service.user_repository.get_by_username_or_email(user_data["username"])
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")

    # Extract role titles for the response
    role_titles = [role.title for role in user_model.roles] if user_model.roles else []

    # Return UserDTO
    return UserDTO(
        id=user_model.id,
        username=user_model.username.value,
        email=user_model.email.value,
        is_active=user_model.is_active,
        roles=role_titles,
        created_at=user_model.created_at,
        updated_at=user_model.updated_at,
    )


from typing import Callable, List, Optional

from fastapi import Depends, HTTPException, status

from app.application.dto.auth_dto import UserDTO
from app.application.interfaces.repositories import RoleRepositoryInterface, UserRepositoryInterface


def authorization_dependency(required: Optional[List[str]] = None):
    """
    Factory function that creates an authorization dependency.
    Accepts a list of required permission strings and returns a dependency
    that checks if the user has the required permissions.
    """

    async def dependency(
        current_user: UserDTO = Depends(get_current_user_from_token),
        user_resource_id: Optional[
            int
        ] = None,  # The ID of the resource being accessed, if applicable
        user_repository: UserRepositoryInterface = Depends(get_user_repository),
        role_repository: RoleRepositoryInterface = Depends(get_role_repository),
    ) -> UserDTO:
        if required is None or len(required) == 0:
            return current_user

        # Check if user is accessing their own resource (self-service)
        if user_resource_id is not None and current_user.id == user_resource_id:
            # User is accessing their own resource, allow basic operations
            # We could implement specific logic here, but for now return the user
            # The original implementation would still apply to non-self resources
            return current_user

        # Get user's roles and their permissions
        user_roles = await role_repository.get_user_roles(current_user.id)
        user_permissions = set()

        # Get all permissions once using PermissionService and create a lookup map
        # In the simplified architecture, we might handle permissions differently
        # For now, using the existing permission service approach
        from app.domain.services.permission_service import PermissionService

        all_permissions = PermissionService.get_permissions()
        permission_map = {perm.id: perm.title for perm in all_permissions}

        # Collect all permissions from user's roles
        for role in user_roles:
            # Get all permission IDs from the role
            for permission_id in role.permissions:
                # Get the permission title from the map and add to user permissions
                permission_title = permission_map.get(permission_id)
                if permission_title:
                    user_permissions.add(permission_title)

        # Check if user has all required permissions
        for required_permission in required:
            if required_permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User does not have required permission: {required_permission}",
                )

        return current_user

    return dependency
