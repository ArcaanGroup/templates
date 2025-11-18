"""Login use case"""

from datetime import timedelta
from typing import Optional

from fastapi import HTTPException, status

from app.application.dto.auth_dto import LoginDTO, TokenDTO, UserDTO
from app.application.interfaces.repositories import UserRepositoryInterface
from app.domain.exceptions.auth_exceptions import (
    AuthenticationFailedException,
    UserNotFoundException,
)
from app.domain.services.auth_service import TokenService, UserService


class LoginUseCase:
    """Use case for user login"""

    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository

    async def execute(self, dto: LoginDTO) -> TokenDTO:
        """Execute the login use case"""
        # Get user by username
        user = await self.user_repository.get_by_username(dto.username)
        if not user:
            raise UserNotFoundException(dto.username)

        # Verify password
        if not UserService.authenticate_user(user, dto.password):
            raise AuthenticationFailedException("Incorrect username or password")

        # Create access token
        access_token = TokenService.create_access_token(subject=user.username.value)

        return TokenDTO(access_token=access_token, token_type="bearer")
