"""Register use case"""

from app.application.dto.auth_dto import RegisterDTO, TokenDTO, UserDTO
from app.application.interfaces.repositories import (
    RefreshTokenRepositoryInterface,
    UserRepositoryInterface,
)
from app.domain.exceptions.auth_exceptions import UserAlreadyExistsException
from app.domain.services.auth_service import TokenService, UserService


class RegisterUseCase:
    """Use case for user registration"""

    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        refresh_token_repository: RefreshTokenRepositoryInterface = None,
    ):
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository

    async def execute(self, dto: RegisterDTO) -> TokenDTO:
        """Execute the user registration use case"""
        # Check if user already exists
        existing_user = await self.user_repository.get_by_username(dto.username)
        if existing_user:
            raise UserAlreadyExistsException(dto.username)

        existing_user = await self.user_repository.get_by_email(dto.email)
        if existing_user:
            raise UserAlreadyExistsException(dto.email)

        # Create the domain user
        user = UserService.create_user(
            username=dto.username, email=dto.email, password=dto.password
        )

        # Save the user
        created_user = await self.user_repository.create(user)

        # Create access and refresh tokens
        access_token = TokenService.create_access_token(subject=created_user.username.value)

        # Create refresh token string
        import secrets

        token_string = secrets.token_urlsafe(32)

        # Create refresh token JWT with the token string as jti
        refresh_token = TokenService.create_refresh_token_with_jti(created_user.id, token_string)

        # Store refresh token in database if repository is provided
        if self.refresh_token_repository:
            from app.domain.entities.refresh_tokens.refresh_token import RefreshToken
            from datetime import timedelta, datetime, timezone
            from app.core.config import settings

            if settings.REFRESH_TOKEN_EXPIRE_MINUTES:
                expires_at = datetime.now(timezone.utc) + timedelta(
                    minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
                )
            else:
                expires_at = datetime.now(timezone.utc) + timedelta(minutes=10080)  # Default 7 days

            refresh_token_entity = RefreshToken(
                token=token_string,  # Store the plain token string in DB
                user_id=created_user.id,
                expires_at=expires_at,
            )
            await self.refresh_token_repository.create(refresh_token_entity)

        return TokenDTO(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
