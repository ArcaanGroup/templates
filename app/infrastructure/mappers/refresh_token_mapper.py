"""
Mapper for converting between RefreshToken domain, DTO, and entity models.
The Entity is the core of conversions
The Entity gets converted from DTO and Entity
And DTO and Entity gets converted from Entity
No Direct conversions from Entity to DTO or DTO to Entity
"""

from app.domain.entities import RefreshTokenEntity
from app.infrastructure.orm import RefreshTokenORM
from app.models import RefreshToken, RefreshTokenCreate


class RefreshTokenMapper:
    """Mapper for converting between RefreshToken domain, DTO, and entity models."""

    @staticmethod
    def to_dto(refresh_token_entity: RefreshTokenEntity) -> RefreshToken:
        """Convert SQLAlchemy entity to DTO."""
        return RefreshToken(
            id=refresh_token_entity.id,
            token=refresh_token_entity.token,
            user_id=refresh_token_entity.user_id,
            expires_at=refresh_token_entity.expires_at,
            created_at=refresh_token_entity.created_at,
            revoked=refresh_token_entity.revoked,
            blacklisted=refresh_token_entity.blacklisted,
        )

    @staticmethod
    def to_create_dto(
        refresh_token_entity: RefreshTokenEntity,
    ) -> RefreshTokenCreate:
        """Convert RefreshToken domain model to DTO."""
        return RefreshTokenCreate(
            user_id=refresh_token_entity.user_id,
            expires_at=refresh_token_entity.expires_at,
        )

    @staticmethod
    def from_orm(
        refresh_token_orm: RefreshTokenORM,
    ) -> RefreshTokenEntity:
        """Convert SQLAlchemy entity to RefreshToken domain model."""
        return RefreshTokenEntity(
            id=refresh_token_orm.id,
            token=refresh_token_orm.token,
            user_id=refresh_token_orm.user_id,
            expires_at=refresh_token_orm.expires_at,
            created_at=refresh_token_orm.created_at,
            revoked=refresh_token_orm.revoked,
            blacklisted=refresh_token_orm.blacklisted,
        )

    @staticmethod
    def to_orm(
        refresh_token_entity: RefreshTokenEntity,
    ) -> RefreshTokenORM:
        """Convert RefreshToken domain model to SQLAlchemy entity."""
        # Create the entity
        orm = RefreshTokenORM(
            id=refresh_token_entity.id,
            token=refresh_token_entity.token,
            user_id=refresh_token_entity.user_id,
            expires_at=refresh_token_entity.expires_at,
            created_at=refresh_token_entity.created_at,
            revoked=refresh_token_entity.revoked,
            blacklisted=refresh_token_entity.blacklisted,
        )

        return orm
