"""Refresh token repository implementation"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_

from app.application.interfaces.repositories import RefreshTokenRepositoryInterface
from app.domain.entities.refresh_tokens.refresh_token import RefreshToken
from app.infrastructure.database.models.refresh_token import RefreshTokenModel


class SQLAlchemyRefreshTokenRepository(RefreshTokenRepositoryInterface):
    """SQLAlchemy implementation of RefreshTokenRepository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: RefreshTokenModel) -> RefreshToken:
        """Convert ORM model to domain entity"""
        from app.domain.entities.refresh_tokens.refresh_token import RefreshToken

        return RefreshToken(
            id=model.id,
            token=model.token,
            user_id=model.user_id,
            expires_at=model.expires_at,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: RefreshToken) -> RefreshTokenModel:
        """Convert domain entity to ORM model"""
        return RefreshTokenModel(
            id=entity.id,
            token=entity.token,
            user_id=entity.user_id,
            expires_at=entity.expires_at,
            is_active=entity.is_active,
        )

    async def create(self, entity: RefreshToken) -> RefreshToken:
        """Create a new refresh token"""
        model = self._to_model(entity)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def get_by_id(self, id: int) -> Optional[RefreshToken]:
        """Get refresh token by ID"""
        result = await self.session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.id == id)
        )
        model = result.scalars().first()
        return self._to_domain(model) if model else None

    async def get_by_token(self, token: str) -> RefreshToken | None:
        """Get refresh token by its value"""
        result = await self.session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.token == token)
        )
        model = result.scalars().first()
        return self._to_domain(model) if model else None

    async def get_active_by_user_id(self, user_id: int) -> list[RefreshToken]:
        """Get all active refresh tokens for a user"""
        result = await self.session.execute(
            select(RefreshTokenModel).where(
                and_(
                    RefreshTokenModel.user_id == user_id,
                    RefreshTokenModel.is_active == True,
                    RefreshTokenModel.expires_at > datetime.utcnow(),
                )
            )
        )
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def deactivate_by_token(self, token: str) -> None:
        """Deactivate a refresh token by its value"""
        result = await self.session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.token == token)
        )
        model = result.scalars().first()
        if model:
            model.is_active = False
            await self.session.commit()

    async def delete_expired_tokens(self) -> int:
        """Delete expired refresh tokens and return the number of deleted tokens"""
        result = await self.session.execute(
            delete(RefreshTokenModel).where(RefreshTokenModel.expires_at < datetime.utcnow())
        )
        await self.session.commit()
        return result.rowcount

    async def update(self, entity: RefreshToken) -> RefreshToken:
        """Update a refresh token"""
        result = await self.session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.id == entity.id)
        )
        model = result.scalars().first()
        if not model:
            raise ValueError(f"Refresh token with id {entity.id} not found")

        model.token = entity.token
        model.user_id = entity.user_id
        model.expires_at = entity.expires_at
        model.is_active = entity.is_active

        await self.session.commit()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def delete(self, entity: RefreshToken) -> None:
        """Delete a refresh token"""
        result = await self.session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.id == entity.id)
        )
        model = result.scalars().first()
        if not model:
            raise ValueError(f"Refresh token with id {entity.id} not found")

        await self.session.delete(model)
        await self.session.commit()
