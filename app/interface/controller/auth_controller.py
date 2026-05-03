import json
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Request, Response

from app.application.use_cases.auth_use_cases import AuthUseCase
from app.application.use_cases.permission_use_cases import PermissionUseCase
from app.infrastructure.core.config import config
from app.infrastructure.dependencies.auth_dependencies import (
    get_auth_service,
    get_authorized_user,
    get_refresh_token_from_cookie,
)
from app.infrastructure.dependencies.permission_dependencies import (
    get_permission_service,
)
from app.infrastructure.error.exceptions import CredentialsValidationException
from app.infrastructure.mappers import PermissionMapper
from app.infrastructure.utils.auth.permission import Permission
from app.interface.dto import Permission as PermissionDTO
from app.interface.dto import Token, User, UserLogin
from app.interface.dto.responses import StandardResponse, failure, success

# Create router with prefix and tags
auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/login", response_model=StandardResponse[Token])
async def login(
    response: Response,
    user_login: UserLogin,
    auth_service: AuthUseCase = Depends(get_auth_service),
):
    """Authenticate user and return JWT token."""
    (access_token, refresh_token) = await auth_service.login(user_login)

    response.set_cookie(
        key=refresh_token.title,
        value=refresh_token.token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="strict",
        max_age=int(timedelta(days=config.refresh_token_expire_days).total_seconds()),
        path="/",
    )

    return success(message="Login successful", payload=access_token)


@auth_router.post("/refresh", response_model=StandardResponse[Token])
async def refresh_tokens(
    auth_service: AuthUseCase = Depends(get_auth_service),
    refresh_token: str = Depends(get_refresh_token_from_cookie),
):
    """Refresh the access token using the refresh token from HTTP-only cookie."""
    # Use the auth service to refresh the access token
    new_token = await auth_service.refresh_access_token(refresh_token)

    return success(message="Token refreshed successfully", payload=new_token)


@auth_router.post("/logout", response_model=StandardResponse[None])
async def logout(
    request: Request,
    response: Response,
    auth_service: AuthUseCase = Depends(get_auth_service),
):
    """Logout the user by blacklisting the refresh token."""
    # Get the refresh token from the cookie
    refresh_token: Optional[str] = request.cookies.get("refresh_token")

    if refresh_token:
        # Blacklist the refresh token in the database
        await auth_service.logout(refresh_token)

        # Clear the refresh token cookie
        response.delete_cookie(key="refresh_token", path="/")

        return success(message="Logged out successfully", payload=None)

    else:
        raise CredentialsValidationException("No refresh token provided")


@auth_router.get("/permissions", response_model=StandardResponse[list[PermissionDTO]])
async def get_permissions(
    permission_service: PermissionUseCase = Depends(get_permission_service),
    _=Depends(get_authorized_user([Permission.Permissions_Read])),
):
    """Return all permissions with their associated policy objects from the JSON files."""
    try:
        # Get permissions from the service (which uses the JSON file)
        permissions_domain = await permission_service.get_all_permissions()

        permissions = [
            PermissionMapper.to_dto(permission).model_dump()
            for permission in permissions_domain
        ]

        # Load policies from JSON file (still needed for full policy objects)
        with open(config.policies_path, "r") as f:
            policies = json.load(f)

        # Create a map of policy ID to policy object for efficient lookups
        policies_map = {policy["id"]: policy for policy in policies}

        # Replace policy IDs in each permission with full policy objects
        for permission in permissions:
            policy_objects = []
            for policy_id in permission.get("policies", []):
                if policy_id in policies_map:
                    policy_objects.append(policies_map[policy_id])
            permission["policies"] = policy_objects

        return success(
            message="Permissions retrieved successfully", payload=permissions
        )
    except FileNotFoundError:
        return failure(message="Permissions or policies file not found", payload=[])
    except json.JSONDecodeError:
        return failure(
            message="Invalid JSON in permissions or policies file", payload=[]
        )


@auth_router.get("/me", response_model=StandardResponse[User])
async def get_me(
    user=Depends(get_authorized_user()),
):
    return success(message="User retrieved successfully", payload=user)
