"""
Mapper for converting between RefreshToken domain, DTO, and entity models.
The Entity is the core of conversions
The Entity gets converted from DTO and Entity
And DTO and Entity gets converted from Entity
No Direct conversions from Entity to DTO or DTO to Entity
"""

from app.domain.entities import RefreshTokenEntity
from app.models.refresh_token.dto import RefreshToken, RefreshTokenCreate
from app.models.refresh_token.entity import RefreshTokenEntity


class RefreshTokenMapper:
    """Mapper for converting between RefreshToken domain, DTO, and entity models."""

    @staticmethod
    def to_dto(refresh_token_domain: RefreshTokenEntity) -> RefreshToken:
        """Convert SQLAlchemy entity to DTO."""
        return RefreshToken(
            id=refresh_token_domain.id,
            token=refresh_token_domain.token,
            user_id=refresh_token_domain.user_id,
            expires_at=refresh_token_domain.expires_at,
            created_at=refresh_token_domain.created_at,
            revoked=refresh_token_domain.revoked,
            blacklisted=refresh_token_domain.blacklisted,
        )

    @staticmethod
    def to_create_dto(
        refresh_token_domain: RefreshTokenEntity,
    ) -> RefreshTokenCreate:
        """Convert RefreshToken domain model to DTO."""
        return RefreshTokenCreate(
            user_id=refresh_token_domain.user_id,
            expires_at=refresh_token_domain.expires_at,
        )

    @staticmethod
    def from_entity(
        refresh_token_entity: RefreshTokenEntity,
    ) -> RefreshTokenEntity:
        """Convert SQLAlchemy entity to RefreshToken domain model."""
        return RefreshTokenEntity(
            id=refresh_token_entity.id,
            token=refresh_token_entity.token,
            user_id=refresh_token_entity.user_id,
            expires_at=refresh_token_entity.expires_at,
            created_at=refresh_token_entity.created_at,
            revoked=refresh_token_entity.revoked,
            blacklisted=refresh_token_entity.blacklisted,
        )

    @staticmethod
    def to_entity(
        refresh_token_domain: RefreshTokenEntity,
    ) -> RefreshTokenEntity:
        """Convert RefreshToken domain model to SQLAlchemy entity."""
        # Create the entity
        entity = RefreshTokenEntity(
            id=refresh_token_domain.id,
            token=refresh_token_domain.token,
            user_id=refresh_token_domain.user_id,
            expires_at=refresh_token_domain.expires_at,
            created_at=refresh_token_domain.created_at,
            revoked=refresh_token_domain.revoked,
            blacklisted=refresh_token_domain.blacklisted,
        )

        return entity
