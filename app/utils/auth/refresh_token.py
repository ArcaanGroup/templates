"""
Refresh token utilities for authentication.
"""

from datetime import datetime, timedelta

from app.core.config import config
from app.models.refresh_token.domain import RefreshTokenDomain


def generate_refresh_token(user_id: str) -> RefreshTokenDomain:
    """
    Generate a new refresh token for the user.

    Args:
        user_id: The ID of the user for whom to generate the token

    Returns:
        RefreshTokenDomain object with the generated token
    """
    expires_at = datetime.utcnow() + timedelta(days=config.refresh_token_expire_days)

    return RefreshTokenDomain.create(user_id=user_id, expires_at=expires_at)
