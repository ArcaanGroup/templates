"""Refresh token use case"""

from datetime import timedelta, datetime, timezone

from jose import JWTError, jwt

from app.application.dto.auth_dto import RefreshTokenDTO, TokenDTO
from app.application.interfaces.repositories import (
    RefreshTokenRepositoryInterface,
    UserRepositoryInterface,
)
from app.core.config import settings
from app.domain.exceptions.auth_exceptions import AuthenticationFailedException
from app.domain.services.auth_service import TokenService


class RefreshTokenUseCase:
    """Use case for refreshing access tokens"""

    def __init__(
        self,
        refresh_token_repository: RefreshTokenRepositoryInterface,
        user_repository: UserRepositoryInterface,
        access_token_expire_minutes: int = None,
    ):
        self._refresh_token_repository = refresh_token_repository
        self._user_repository = user_repository
        self._access_token_expire_minutes = access_token_expire_minutes

    async def execute(self, dto: RefreshTokenDTO) -> TokenDTO:
        """Execute the refresh token use case"""
        # First, decode the refresh token JWT to extract the jti (token ID)
        try:
            # Decode without verification to get the jti
            payload = jwt.decode(
                dto.refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
                options={"verify_signature": False},
            )
            user_id_str = payload.get("sub")
            token_type = payload.get("type")
            jti = payload.get("jti")

            if not user_id_str or token_type != "refresh" or not jti:
                raise AuthenticationFailedException("Invalid refresh token")

            # Now verify the token signature
            payload = jwt.decode(
                dto.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            user_id_str = payload.get("sub")
            token_type = payload.get("type")
            jti = payload.get("jti")

            if not user_id_str or token_type != "refresh" or not jti:
                raise AuthenticationFailedException("Invalid refresh token")
        except JWTError:
            raise AuthenticationFailedException("Invalid refresh token")

        try:
            user_id = int(user_id_str)
        except ValueError:
            raise AuthenticationFailedException("Invalid refresh token")

        # Retrieve the refresh token from the database using the jti
        db_refresh_token = await self._refresh_token_repository.get_by_token(jti)
        if (
            not db_refresh_token
            or not db_refresh_token.is_valid()
            or db_refresh_token.user_id != user_id
        ):
            raise AuthenticationFailedException("Refresh token not found or invalid in database")

        # Get the user to ensure they still exist and are active
        user = await self._user_repository.get_by_id(user_id)
        if not user or not user.is_active:
            raise AuthenticationFailedException("User not found or deactivated")

        # Generate new access and refresh tokens
        new_access_token = TokenService.create_access_token(
            subject=user.username.value,
            expires_delta=timedelta(minutes=self._access_token_expire_minutes)
            if self._access_token_expire_minutes
            else None,
        )
        new_refresh_token = TokenService.create_refresh_token(user.id)

        # Create new refresh token string for database storage
        import secrets

        new_token_string = secrets.token_urlsafe(32)

        # Create JWT for the client with the token string as jti
        new_refresh_token = TokenService.create_refresh_token_with_jti(user.id, new_token_string)

        # Store the new refresh token in the database
        from app.domain.entities.refresh_tokens.refresh_token import RefreshToken

        if settings.REFRESH_TOKEN_EXPIRE_MINUTES:
            expires_at = datetime.now(timezone.utc) + timedelta(
                minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
            )
        else:
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=10080)  # Default 7 days

        new_db_refresh_token = RefreshToken(
            token=new_token_string,  # Store the plain token string in DB
            user_id=user.id,
            expires_at=expires_at,
        )
        await self._refresh_token_repository.create(new_db_refresh_token)

        # Deactivate the old refresh token
        db_refresh_token.deactivate()
        await self._refresh_token_repository.update(db_refresh_token)

        # Return the new tokens
        return TokenDTO(
            access_token=new_access_token, refresh_token=new_refresh_token, token_type="bearer"
        )
