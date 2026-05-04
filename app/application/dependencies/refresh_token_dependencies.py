"""
Refresh token-related dependencies and dependency injection logic.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.core.database import get_db_session
from app.infrastructure.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.interface.repository.refresh_token_repository_interface import (
    IRefreshTokenRepository,
)


async def get_refresh_token_repository(
    db_session: AsyncSession = Depends(get_db_session),
) -> IRefreshTokenRepository:
    """Dependency to get refresh token repository instance."""
    return RefreshTokenRepository(db_session)
