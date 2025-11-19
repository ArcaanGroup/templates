"""Logout use case"""

from typing import Optional

from jose import JWTError, jwt

from app.application.interfaces.repositories import RefreshTokenRepositoryInterface
from app.core.config import settings
from app.domain.exceptions.auth_exceptions import AuthenticationFailedException
from app.domain.services.auth_service import TokenService


class LogoutUseCase:
    """Use case for user logout (invalidate refresh tokens)"""

    def __init__(self, refresh_token_repository: RefreshTokenRepositoryInterface):
        self._refresh_token_repository = refresh_token_repository

    async def execute(self, token: Optional[str] = None) -> bool:
        """Execute the logout use case - invalidate the provided refresh token"""
        if not token:
            # If no token provided, we can't invalidate anything
            return True

        # Decode the JWT to extract the jti (token ID)
        try:
            # Decode without verification to get the jti
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
                options={"verify_signature": False},
            )
            user_id_str = payload.get("sub")
            token_type = payload.get("type")
            jti = payload.get("jti")

            if not user_id_str or token_type != "refresh" or not jti:
                # If the token format is invalid, we consider logout successful
                return True

            # Now verify the token signature
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id_str = payload.get("sub")
            token_type = payload.get("type")
            jti = payload.get("jti")

            if not user_id_str or token_type != "refresh" or not jti:
                # If the token format is invalid, we consider logout successful
                return True
        except JWTError:
            # If the token is invalid, we consider logout successful
            return True

        try:
            user_id = int(user_id_str)
        except ValueError:
            # If the user ID is invalid, we consider logout successful
            return True

        # Find and deactivate the refresh token in the database using jti
        db_refresh_token = await self._refresh_token_repository.get_by_token(jti)
        if db_refresh_token and db_refresh_token.user_id == user_id:
            # Deactivate the refresh token
            db_refresh_token.deactivate()
            await self._refresh_token_repository.update(db_refresh_token)

        return True
