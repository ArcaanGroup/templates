"""
Implementation of the refresh token repository using SQLAlchemy.
This is the concrete repository implementation for PostgreSQL database.
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.domain.entities import RefreshTokenEntity
from app.infrastructure.db.orm import RefreshTokenORM
from app.infrastructure.mappers import RefreshTokenMapper
from app.interface.repository.refresh_token_repository_interface import (
    IRefreshTokenRepository,
)


class RefreshTokenRepository(IRefreshTokenRepository):
    """Implementation of refresh token repository operations using SQLAlchemy."""

    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def create_refresh_token(
        self, refresh_token_to_create: RefreshTokenEntity
    ) -> RefreshTokenEntity:
        """Create a new refresh token in the repository."""

        # Create SQLAlchemy RefreshToken object from domain entity
        refresh_token_orm = RefreshTokenMapper.to_orm(refresh_token_to_create)

        self.session.add(refresh_token_orm)
        await self.session.commit()
        await self.session.refresh(refresh_token_orm)

        # Convert to domain entity for return to match interface
        return RefreshTokenMapper.from_orm(refresh_token_orm)

    async def get_refresh_token_by_token(
        self, token: str
    ) -> Optional[RefreshTokenEntity]:
        """Get a refresh token by its token value from the repository."""
        result = await self.session.execute(
            select(RefreshTokenORM).where(
                RefreshTokenORM.token == token,
            )
        )
        refresh_token_orm = result.scalar_one_or_none()

        if not refresh_token_orm:
            return None

        return RefreshTokenMapper.from_orm(refresh_token_orm)

    async def revoke_refresh_token(self, token_id: str) -> bool:
        """Revoke a refresh token in the repository."""
        result = await self.session.execute(
            select(RefreshTokenORM).where(RefreshTokenORM.id == token_id)
        )
        refresh_token_orm = result.scalar_one_or_none()

        if not refresh_token_orm:
            return False

        await self.session.delete(refresh_token_orm)
        await self.session.commit()

        return True
