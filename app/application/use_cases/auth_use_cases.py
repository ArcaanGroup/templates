"""
True Clean Architecture Use Cases for Authentication operations.
Use cases contain business logic and are independent of frameworks and external concerns.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from app.domain.entities import RefreshTokenEntity, UserEntity
from app.domain.error.exceptions import (
    CredentialsValidationException,
    InactiveUserException,
    ResourceNotFoundException,
)
from app.interface.repository.refresh_token_repository_interface import (
    IRefreshTokenRepository,
)
from app.interface.repository.user_repository_interface import IUserRepository


@dataclass(frozen=True)
class LoginRequest:
    """Input port for user login."""
    username: str
    password: str


@dataclass(frozen=True)
class TokenResponse:
    """Output port for token information."""
    title: str
    token: str
    type: str
    expires_at: datetime


@dataclass(frozen=True)
class LoginResponse:
    """Output port for login."""
    access_token: TokenResponse
    refresh_token: TokenResponse


@dataclass(frozen=True)
class RefreshTokenRequest:
    """Input port for refreshing access token."""
    refresh_token: str


@dataclass(frozen=True)
class RefreshTokenResponse:
    """Output port for refreshed access token."""
    access_token: TokenResponse


@dataclass(frozen=True)
class LogoutRequest:
    """Input port for logout."""
    refresh_token: str


@dataclass(frozen=True)
class LogoutResponse:
    """Output port for logout."""
    success: bool


class AuthenticateUserUseCase:
    """Use case for authenticating a user."""

    def __init__(
        self,
        user_repository: IUserRepository,
        password_service: "IPasswordService",
    ):
        self._user_repo = user_repository
        self._password_service = password_service

    async def execute(self, username: str, password: str) -> UserEntity:
        """Execute the use case to authenticate a user."""
        user = await self._user_repo.get_by_username(username)
        if not user or not self._password_service.verify(
            password, user.hashed_password
        ):
            raise CredentialsValidationException("Incorrect username or password")

        if not user.is_active:
            raise InactiveUserException()

        return user


class LoginUseCase:
    """Use case for user login."""

    def __init__(
        self,
        authenticate_use_case: AuthenticateUserUseCase,
        token_service: "ITokenService",
        refresh_token_repository: IRefreshTokenRepository,
    ):
        self._authenticate_use_case = authenticate_use_case
        self._token_service = token_service
        self._refresh_token_repo = refresh_token_repository

    async def execute(self, request: LoginRequest) -> LoginResponse:
        """Execute the use case to login a user."""
        user = await self._authenticate_use_case.execute(
            request.username, request.password
        )

        # Generate access token
        access_token_str = self._token_service.generate_access_token(
            data={"sub": user.id, "username": user.username},
        )
        access_expires_at = datetime.utcnow() + timedelta(
            minutes=self._token_service.access_token_expire_minutes
        )
        access_token = TokenResponse(
            title="access_token",
            token=access_token_str,
            type="bearer",
            expires_at=access_expires_at,
        )

        # Generate refresh token
        refresh_token_entity = self._token_service.generate_refresh_token(user.id)
        refresh_token_dto = await self._refresh_token_repo.create_refresh_token(
            refresh_token_entity
        )
        refresh_token = TokenResponse(
            title="refresh_token",
            token=refresh_token_dto.token,
            type="cookie",
            expires_at=refresh_token_dto.expires_at,
        )

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )


class RefreshAccessTokenUseCase:
    """Use case for refreshing an access token."""

    def __init__(
        self,
        refresh_token_repository: IRefreshTokenRepository,
        user_repository: IUserRepository,
        token_service: "ITokenService",
    ):
        self._refresh_token_repo = refresh_token_repository
        self._user_repo = user_repository
        self._token_service = token_service

    async def execute(self, request: RefreshTokenRequest) -> RefreshTokenResponse:
        """Execute the use case to refresh an access token."""
        refresh_token_entity = await self._refresh_token_repo.get_refresh_token_by_token(
            request.refresh_token
        )

        if not refresh_token_entity or not refresh_token_entity.is_valid():
            raise CredentialsValidationException("Invalid refresh token")

        user = await self._user_repo.get_by_id(refresh_token_entity.user_id)
        if not user:
            raise CredentialsValidationException("Invalid refresh token")
        elif not user.is_active:
            await self._refresh_token_repo.revoke_refresh_token(
                refresh_token_entity.id
            )
            raise InactiveUserException()

        access_token_str = self._token_service.generate_access_token(
            data={"sub": user.id, "username": user.username},
        )
        access_expires_at = datetime.utcnow() + timedelta(
            minutes=self._token_service.access_token_expire_minutes
        )
        access_token = TokenResponse(
            title="access_token",
            token=access_token_str,
            type="bearer",
            expires_at=access_expires_at,
        )

        return RefreshTokenResponse(access_token=access_token)


class LogoutUseCase:
    """Use case for logging out a user."""

    def __init__(
        self,
        refresh_token_repository: IRefreshTokenRepository,
    ):
        self._refresh_token_repo = refresh_token_repository

    async def execute(self, request: LogoutRequest) -> LogoutResponse:
        """Execute the use case to logout a user."""
        refresh_token_entity = await self._refresh_token_repo.get_refresh_token_by_token(
            request.refresh_token
        )

        if not refresh_token_entity:
            return LogoutResponse(success=False)

        success = await self._refresh_token_repo.revoke_refresh_token(
            refresh_token_entity.id
        )
        return LogoutResponse(success=success)


# Service interfaces for dependency inversion
class IPasswordService:
    """Interface for password operations."""

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        raise NotImplementedError


class ITokenService:
    """Interface for token operations."""

    @property
    def access_token_expire_minutes(self) -> int:
        """Get access token expiration in minutes."""
        raise NotImplementedError

    def generate_access_token(self, data: dict) -> str:
        """Generate an access token."""
        raise NotImplementedError

    def generate_refresh_token(self, user_id: str) -> RefreshTokenEntity:
        """Generate a refresh token entity."""
        raise NotImplementedError
