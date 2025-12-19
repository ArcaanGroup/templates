"""
Authentication service for handling login and token management.
"""

from datetime import datetime, timedelta
from typing import Optional

from app.core import config
from app.error.exceptions import CredentialsValidationException, InactiveUserException
from app.interface.repositories.refresh_token_repository_interface import (
    IRefreshTokenRepository,
)
from app.interface.repositories.user_repository_interface import IUserRepository
from app.models.auth.dto import Token, UserLogin
from app.models.user.dto import User
from app.models.user.mapper import UserMapper
from app.utils import verify_password
from app.utils.auth import generate_access_token, generate_refresh_token


class AuthService:
    """
    Service layer for authentication operations.
    Contains business logic for user authentication.
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        refresh_token_repository: IRefreshTokenRepository,
    ):
        self.user_repo = user_repository
        self.refresh_token_repo = refresh_token_repository

    async def authenticate_user(self, username: str, password: str) -> User:
        """
        Authenticate a user with username and password.

        Args:
            username: The user's username
            password: The user's plain text password

        Returns:
            User object if authentication is successful, None otherwise
        """
        # Get user domain entity to access the hashed password
        domain_user = await self.user_repo.get_by_username(username)
        if not domain_user or not verify_password(
            password, domain_user.hashed_password
        ):
            raise CredentialsValidationException("Incorrect username or password")

        if not domain_user.is_active:
            raise InactiveUserException()

        # Convert domain entity to DTO for return to maintain the expected interface

        return UserMapper.to_dto(domain_user)

    async def login(
        self, user_login: UserLogin
    ) -> tuple[Token, Token]:  # returns: (access_token, refresh_token)
        """
        Handle user login and return JWT token and refresh token.

        Args:
            user_login: Login credentials from request

        Returns:
            Token containing the access token and refresh token info
        """
        user = await self.authenticate_user(user_login.username, user_login.password)

        # Generate access token
        access_token = generate_access_token(
            data={"sub": user.id, "username": user.username},
        )

        # Generate refresh token
        refresh_token_domain = generate_refresh_token(user.id)
        refresh_token_dto = await self.refresh_token_repo.create_refresh_token(
            refresh_token_domain
        )

        # Convert to DTO
        access_token_expires_at = datetime.utcnow() + timedelta(
            minutes=config.access_token_expire_minutes
        )
        access_token = Token(
            title="access_token",
            token=access_token,
            type="bearer",
            expires_at=access_token_expires_at,
        )
        refresh_token = Token(
            title="refresh_token",
            token=refresh_token_dto.token,
            type="cookie",
            expires_at=refresh_token_dto.expires_at,
        )

        return (access_token, refresh_token)

    async def refresh_access_token(self, refresh_token: str) -> Optional[Token]:
        """
        Refresh the access token using the refresh token.

        Args:
            refresh_token: The refresh token string

        Returns:
            New access token if refresh is successful, None otherwise
        """
        # Get the refresh token from the repository
        refresh_token_domain = await self.refresh_token_repo.get_refresh_token_by_token(
            refresh_token
        )

        if not refresh_token_domain or not refresh_token_domain.is_valid():
            raise CredentialsValidationException("Invalid refresh token")

        # Get the user to make sure they exist and are active
        user = await self.user_repo.get_by_id(refresh_token_domain.user_id)
        if not user:
            raise CredentialsValidationException("Invalid refresh token")
        elif not user.is_active:
            # If the user doesn't exist or is inactive, revoke the refresh token
            await self.refresh_token_repo.revoke_refresh_token(refresh_token_domain.id)
            raise InactiveUserException()

        # Generate a new access token
        access_token = generate_access_token(
            data={"sub": user.id, "username": user.username},
        )
        access_token_expires_at = datetime.utcnow() + timedelta(
            config.access_token_expire_minutes
        )
        return Token(
            title="access_token",
            token=access_token,
            type="bearer",
            expires_at=access_token_expires_at,
        )

    async def logout(self, refresh_token: str) -> bool:
        """
        Logout the user by blacklisting the refresh token.

        Args:
            refresh_token: The refresh token to blacklist

        Returns:
            True if logout was successful, False otherwise
        """
        refresh_token_domain = await self.refresh_token_repo.get_refresh_token_by_token(
            refresh_token
        )

        if not refresh_token_domain:
            return False

        # Blacklist the refresh token so it can't be used again
        result = await self.refresh_token_repo.revoke_refresh_token(
            refresh_token_domain.id
        )
        return result
