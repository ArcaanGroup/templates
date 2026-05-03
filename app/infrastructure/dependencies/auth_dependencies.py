"""
Authentication-related dependencies and dependency injection logic.
"""

from typing import List, Optional

from fastapi import Cookie, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.application.use_cases.auth_use_cases import AuthUseCase
from app.application.use_cases.policy_engine_use_cases import PolicyEngineUseCase
from app.domain.entities import RoleEntity
from app.infrastructure.core.config import config
from app.infrastructure.dependencies.policy_dependencies import (
    get_policy_engine_service,
)
from app.infrastructure.dependencies.refresh_token_dependencies import (
    get_refresh_token_repository,
)
from app.infrastructure.dependencies.role_dependencies import get_role_repository
from app.infrastructure.error.exceptions import (
    CredentialsValidationException,
    InactiveUserException,
    UnauthorizedException,
)
from app.infrastructure.mappers import UserMapper
from app.infrastructure.utils.auth.permission import Permission
from app.interface.dto import TokenData, User
from app.interface.repositories.role_repository_interface import IRoleRepository
from app.interface.repositories.user_repository_interface import IUserRepository

from .user_dependencies import get_user_repository

SECRET_KEY = config.secret_key
ALGORITHM = config.algorithm


security = HTTPBearer(auto_error=False)


def get_refresh_token_from_cookie(
    refresh_token: str = Cookie(None, alias="refresh_token"),
):
    """Extracts the refresh token from corresponding cookie"""
    if not refresh_token:
        raise CredentialsValidationException("No refresh token provided")
    return refresh_token


def verify_token(token: str) -> Optional[TokenData]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string to verify

    Returns:
        TokenData if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Validate that required fields exist
        sub = payload.get("sub")
        username = payload.get("username")

        if sub is None or username is None:
            return None

        token_data = TokenData(
            sub=sub,
            username=username,
        )

        return token_data
    except JWTError:
        return None


async def authorize(
    required_permissions: List[Permission] = [],
    access_token: HTTPAuthorizationCredentials = Depends(security),
    user_repository: IUserRepository = Depends(get_user_repository),
    role_repository: IRoleRepository = Depends(get_role_repository),
    policy_engine_service: PolicyEngineUseCase = Depends(get_policy_engine_service),
) -> Optional[User]:
    """
    Get the current user from the token in the request and check required permissions.

    Args:
        required_permissions: List of permissions required to access the resource
        credentials: HTTP authorization credentials from the request
        user_repository: User repository for database access
        role_repository: Role repository for database access

    Returns:
        UserEntity object if token is valid and user has required permissions, raises HTTPException otherwise
    """
    # Authentication --------------------
    if not access_token.credentials:
        raise CredentialsValidationException("No access token provided")

    token_data = verify_token(access_token.credentials)

    if token_data is None or token_data.username is None:
        raise CredentialsValidationException()

    # Get user entity from the database using the username from the token
    # We use the entity method to get the full user with hashed password for domain creation
    user_domain = await user_repository.get_by_username(token_data.username)
    if user_domain is None:
        raise CredentialsValidationException()

    if not user_domain.is_active:
        raise InactiveUserException()

    # Convert entity to DTO
    user_dto = UserMapper.to_dto(user_domain)
    # -------------------- Authentication

    # Authorization --------------------

    # If required permissions are specified, check if the user has them
    if required_permissions:
        # Get all roles assigned to the user
        user_role_ids = [role.id for role in user_dto.roles] if user_dto.roles else []

        # Fetch all user roles with their permission_ids
        user_roles: list[RoleEntity] = []
        for role_id in user_role_ids:
            role = await role_repository.get_by_id(role_id)
            if role:
                user_roles.append(role)

        # Collect all permissions from all user roles
        all_user_permission_ids = set()
        for role in user_roles:
            if role.permission_ids:
                all_user_permission_ids.update(role.permission_ids)

        # Skip permissions check for super users
        if Permission.Super_User.value not in all_user_permission_ids:
            # Check if user has all required permissions
            required_permission_ids = [perm.value for perm in required_permissions]
            for perm_id in required_permission_ids:
                if perm_id not in all_user_permission_ids:
                    raise UnauthorizedException()
    # -------------------- Authorization

    return user_dto


def get_authorized_user(required_permissions: List[Permission] = []):
    """
    Factory function to create a permission checker with specific permissions.

    Args:
        required_permissions: List of permissions required for the endpoint

    Returns:
        A function that can be used with FastAPI's Depends
    """

    async def authorize_dependency(
        access_token: Optional[HTTPAuthorizationCredentials] = Depends(security),
        user_repository: IUserRepository = Depends(get_user_repository),
        role_repository: IRoleRepository = Depends(get_role_repository),
        policy_engine_service: PolicyEngineUseCase = Depends(get_policy_engine_service),
    ) -> Optional[User]:
        if access_token is None:
            raise CredentialsValidationException()

        return await authorize(
            access_token=access_token,
            required_permissions=required_permissions,
            user_repository=user_repository,
            role_repository=role_repository,
            policy_engine_service=policy_engine_service,
        )

    return authorize_dependency


async def get_auth_service(
    user_repository: IUserRepository = Depends(get_user_repository),
    refresh_token_repository=Depends(get_refresh_token_repository),
) -> AuthUseCase:
    """Dependency to get auth service instance."""
    return AuthUseCase(user_repository, refresh_token_repository)
