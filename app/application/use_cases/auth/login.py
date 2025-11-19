"""Login use case"""

from datetime import timedelta

from app.application.dto.auth_dto import LoginDTO, TokenDTO, UserDTO
from app.application.interfaces.repositories import (
    RefreshTokenRepositoryInterface,
    UserRepositoryInterface,
)
from app.domain.exceptions.auth_exceptions import (
    AuthenticationFailedException,
    UserNotFoundException,
)
from app.domain.services.auth_service import TokenService, UserService


class LoginUseCase:
    """Use case for user login"""

    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        refresh_token_repository: RefreshTokenRepositoryInterface = None,
    ):
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository

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

        # Create refresh token string
        import secrets

        token_string = secrets.token_urlsafe(32)

        # Create refresh token JWT with the token string as jti
        refresh_token = TokenService.create_refresh_token_with_jti(user.id, token_string)

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
                user_id=user.id,
                expires_at=expires_at,
            )
            await self.refresh_token_repository.create(refresh_token_entity)

        return TokenDTO(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
