"""
Implementation of the refresh token repository using SQLAlchemy.
This is the concrete repository implementation for PostgreSQL database.
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.interface.repositories.refresh_token_repository_interface import (
    IRefreshTokenRepository,
)
from app.models.refresh_token.domain import RefreshTokenDomain
from app.models.refresh_token.dto import RefreshTokenCreate
from app.models.refresh_token.entity import RefreshTokenEntity
from app.models.refresh_token.mapper import RefreshTokenMapper


class RefreshTokenRepository(IRefreshTokenRepository):
    """Implementation of refresh token repository operations using SQLAlchemy."""

    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def create_refresh_token(
        self, refresh_token_to_create: RefreshTokenDomain
    ) -> RefreshTokenDomain:
        """Create a new refresh token in the repository."""

        # Create SQLAlchemy RefreshToken object from domain entity
        refresh_token_entity = RefreshTokenMapper.to_entity(refresh_token_to_create)

        self.session.add(refresh_token_entity)
        await self.session.commit()
        await self.session.refresh(refresh_token_entity)

        # Convert to domain entity for return to match interface
        return RefreshTokenMapper.from_entity(refresh_token_entity)

    async def get_refresh_token_by_token(
        self, token: str
    ) -> Optional[RefreshTokenDomain]:
        """Get a refresh token by its token value from the repository."""
        result = await self.session.execute(
            select(RefreshTokenEntity).where(
                RefreshTokenEntity.token == token,
            )
        )
        db_refresh_token = result.scalar_one_or_none()

        if not db_refresh_token:
            return None

        return RefreshTokenMapper.from_entity(db_refresh_token)

    async def revoke_refresh_token(self, token_id: str) -> bool:
        """Revoke a refresh token in the repository."""
        result = await self.session.execute(
            select(RefreshTokenEntity).where(RefreshTokenEntity.id == token_id)
        )
        db_refresh_token = result.scalar_one_or_none()

        if not db_refresh_token:
            return False

        await self.session.delete(db_refresh_token)
        await self.session.commit()

        return True
