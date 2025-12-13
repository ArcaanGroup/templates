"""
Authentication-related dependencies and dependency injection logic.
"""

from typing import List, Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import config
from app.dependencies.refresh_token_dependencies import (
    get_refresh_token_repository,
)
from app.dependencies.role_dependencies import get_role_repository
from app.error.exceptions import (
    CredentialsValidationException,
    InactiveUserException,
    UnauthorizedException,
)
from app.interface.repositories.role_repository_interface import IRoleRepository
from app.interface.repositories.user_repository_interface import IUserRepository
from app.models.auth.dto import TokenData
from app.models.user.dto import User
from app.models.user.mapper import UserMapper
from app.service.auth_service import AuthService
from app.utils.auth.permission import Permission

from .user_dependencies import get_user_repository

SECRET_KEY = config.secret_key
ALGORITHM = config.algorithm


security = HTTPBearer(auto_error=False)


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
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    user_repository: IUserRepository = Depends(get_user_repository),
    role_repository: IRoleRepository = Depends(get_role_repository),
) -> Optional[User]:
    """
    Get the current user from the token in the request and check required permissions.

    Args:
        required_permissions: List of permissions required to access the resource
        credentials: HTTP authorization credentials from the request
        user_repository: User repository for database access
        role_repository: Role repository for database access

    Returns:
        UserDomain object if token is valid and user has required permissions, raises HTTPException otherwise
    """
    if not credentials:
        raise CredentialsValidationException()

    token = credentials.credentials
    token_data = verify_token(token)

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

    # If required permissions are specified, check if the user has them
    if required_permissions:
        # Get all roles assigned to the user
        user_role_ids = [role.id for role in user_dto.roles] if user_dto.roles else []

        # Fetch all user roles with their permission_ids
        user_roles = []
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

    return user_dto


def get_authorized_user(required_permissions: List[Permission]):
    """
    Factory function to create a permission checker with specific permissions.

    Args:
        required_permissions: List of permissions required for the endpoint

    Returns:
        A function that can be used with FastAPI's Depends
    """

    async def get_authorized_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        user_repository: IUserRepository = Depends(get_user_repository),
        role_repository: IRoleRepository = Depends(get_role_repository),
    ) -> Optional[User]:
        return await authorize(
            required_permissions=required_permissions,
            credentials=credentials,
            user_repository=user_repository,
            role_repository=role_repository,
        )

    return get_authorized_user


async def get_auth_service(
    user_repository: IUserRepository = Depends(get_user_repository),
    refresh_token_repository=Depends(get_refresh_token_repository),
) -> AuthService:
    """Dependency to get auth service instance."""
    return AuthService(user_repository, refresh_token_repository)
