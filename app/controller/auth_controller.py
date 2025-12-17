import json
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Request, Response

from app.core.config import config
from app.dependencies.auth_dependencies import (
    get_auth_service,
    get_authorized_user,
)
from app.dependencies.permission_dependencies import get_permission_service
from app.error.exceptions import (
    CredentialsValidationException,
    DomainException,
)
from app.models.auth.dto import UserLogin
from app.models.permission.mapper import PermissionMapper
from app.models.responses import StandardResponse, failure, success
from app.models.user.dto import User
from app.service.auth_service import AuthService
from app.service.permission_service import PermissionService
from app.utils.auth.permission import Permission

# Create router with prefix and tags
auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/login", response_model=StandardResponse[None])
async def login(
    response: Response,
    user_login: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Authenticate user and return JWT token."""
    token = await auth_service.login(user_login)

    if token.refresh_token is None:
        raise DomainException("Something went wrong")

    # Set the refresh token in an HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="strict",  # Adjust as needed
        max_age=int(
            timedelta(minutes=15).total_seconds()
        ),  # Same as refresh token expiration
        path="/",
    )

    # Set the refresh token in an HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=token.refresh_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="strict",  # Adjust as needed
        max_age=int(
            timedelta(days=7).total_seconds()
        ),  # Same as refresh token expiration
        path="/api/auth/refresh",  # Limit the cookie to the refresh endpoint path
    )

    return success(message="Login successful")


@auth_router.post("/refresh", response_model=StandardResponse[None])
async def refresh_tokens(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Refresh the access token using the refresh token from HTTP-only cookie."""
    # Get the refresh token from the cookie
    refresh_token: Optional[str] = request.cookies.get("refresh_token")

    if not refresh_token:
        raise CredentialsValidationException(message="No refresh token provided")

    # Use the auth service to refresh the access token
    new_token = await auth_service.refresh_access_token(refresh_token)

    if not new_token or not new_token.refresh_token:
        raise CredentialsValidationException(detail="Invalid or expired refresh token")

    # Update the refresh token cookie if needed (in case it's rotated)
    response.set_cookie(
        key="refresh_token",
        value=new_token.refresh_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=int(
            timedelta(days=7).total_seconds()
        ),  # Same as refresh token expiration
        path="/auth/refresh",  # Limit the cookie to the refresh endpoint path
    )

    # Also update the access token cookie with the new token
    response.set_cookie(
        key="access_token",
        value=new_token.access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="strict",
        max_age=int(
            timedelta(minutes=15).total_seconds()
        ),  # Same as access token expiration
        path="/",
    )

    return success(message="Token refreshed successfully")


@auth_router.post("/logout", response_model=StandardResponse[None])
async def logout(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Logout the user by blacklisting the refresh token."""
    # Get the refresh token from the cookie
    refresh_token: Optional[str] = request.cookies.get("refresh_token")

    if refresh_token:
        # Blacklist the refresh token in the database
        await auth_service.logout(refresh_token)

    # Clear the refresh token cookie
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/auth/refresh")

    return success(message="Logged out successfully", payload=None)


@auth_router.get("/permissions", response_model=StandardResponse[list[Permission]])
async def get_permissions(
    permission_service: PermissionService = Depends(get_permission_service),
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
    user=Depends(get_authorized_user([])),
):
    return success(message="User retrieved successfully", payload=user)
