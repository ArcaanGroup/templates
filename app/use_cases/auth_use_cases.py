from datetime import datetime, timedelta
from typing import Optional

from app.core import config
from app.error.exceptions import CredentialsValidationException, InactiveUserException
from app.infrastructure.mappers import UserMapper
from app.interface.repositories.refresh_token_repository_interface import (
    IRefreshTokenRepository,
)
from app.interface.repositories.user_repository_interface import IUserRepository
from app.models import Token, UserLogin
from app.utils import verify_password
from app.utils.auth import generate_access_token, generate_refresh_token


class AuthUseCase:
    """Use case layer for authentication operations."""

    def __init__(
        self,
        user_repository: IUserRepository,
        refresh_token_repository: IRefreshTokenRepository,
    ):
        self.user_repo = user_repository
        self.refresh_token_repo = refresh_token_repository

    async def authenticate_user(self, username: str, password: str):
        domain_user = await self.user_repo.get_by_username(username)
        if not domain_user or not verify_password(
            password, domain_user.hashed_password
        ):
            raise CredentialsValidationException("Incorrect username or password")

        if not domain_user.is_active:
            raise InactiveUserException()

        return UserMapper.to_dto(domain_user)

    async def login(self, user_login: UserLogin) -> tuple[Token, Token]:
        user = await self.authenticate_user(user_login.username, user_login.password)

        access_token = generate_access_token(
            data={"sub": user.id, "username": user.username},
        )

        refresh_token_domain = generate_refresh_token(user.id)
        refresh_token_dto = await self.refresh_token_repo.create_refresh_token(
            refresh_token_domain
        )

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
        refresh_token_domain = await self.refresh_token_repo.get_refresh_token_by_token(
            refresh_token
        )

        if not refresh_token_domain or not refresh_token_domain.is_valid():
            raise CredentialsValidationException("Invalid refresh token")

        user = await self.user_repo.get_by_id(refresh_token_domain.user_id)
        if not user:
            raise CredentialsValidationException("Invalid refresh token")
        elif not user.is_active:
            await self.refresh_token_repo.revoke_refresh_token(refresh_token_domain.id)
            raise InactiveUserException()

        access_token = generate_access_token(
            data={"sub": user.id, "username": user.username},
        )
        access_token_expires_at = datetime.utcnow() + timedelta(
            minutes=config.access_token_expire_minutes
        )
        return Token(
            title="access_token",
            token=access_token,
            type="bearer",
            expires_at=access_token_expires_at,
        )

    async def logout(self, refresh_token: str) -> bool:
        refresh_token_domain = await self.refresh_token_repo.get_refresh_token_by_token(
            refresh_token
        )

        if not refresh_token_domain:
            return False

        return await self.refresh_token_repo.revoke_refresh_token(
            refresh_token_domain.id
        )
