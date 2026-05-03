"""
Role Mapper - handles conversion between RoleEntity, RoleEntity, and Role DTO
The Entity is the core of conversions
The Entity gets converted from DTO and Entity
And DTO and Entity gets converted from Entity
No Direct conversions from Entity to DTO or DTO to Entity
"""

from datetime import datetime

from app.domain.entities import RoleEntity
from app.models.role.dto import Role as RoleDTO
from app.models.role.dto import RoleCreate, RoleUpdate
from app.models.role.entity import RoleEntity


class RoleMapper:
    """Mapper class to handle conversions between Role representations."""

    @staticmethod
    def from_dto(dto: RoleCreate) -> RoleEntity:
        """Convert DTO Role to domain."""
        return RoleEntity.create(
            name=dto.name,
            permission_ids=dto.permission_ids,
        )

    @staticmethod
    def to_dto(domain_role: RoleEntity) -> RoleDTO:
        """Convert domain Role to DTO."""
        return RoleDTO(
            id=domain_role.id,
            name=domain_role.name,
            created_at=domain_role.created_at,
            updated_at=domain_role.updated_at,
            is_active=domain_role.is_active,
            permission_ids=domain_role.permission_ids or [],
        )

    @staticmethod
    def from_entity(entity_role: RoleEntity) -> RoleEntity:
        """Convert entity Role to domain."""
        return RoleEntity(
            id=entity_role.id,
            name=entity_role.name,
            created_at=entity_role.created_at,
            updated_at=entity_role.updated_at,
            is_active=entity_role.is_active,
            permission_ids=entity_role.permission_ids or [],
        )

    @staticmethod
    def to_entity(domain_role: RoleEntity) -> RoleEntity:
        """Convert domain Role to entity."""
        entity = RoleEntity(
            id=domain_role.id,
            name=domain_role.name,
            created_at=domain_role.created_at,
            updated_at=domain_role.updated_at,
            is_active=domain_role.is_active,
            permission_ids=domain_role.permission_ids or [],
        )
        # Note: The users relationship is handled by SQLAlchemy's ORM when the entity is loaded
        # The many-to-many relationship will be established when the entity is saved to the database
        return entity

    @staticmethod
    def update_from_dto(role_update: RoleUpdate, role_domain: RoleEntity) -> RoleEntity:
        """Apply RoleUpdate DTO to an existing RoleEntity and return updated domain entity."""
        update_data = {
            k: v for k, v in role_update.model_dump().items() if v is not None
        }

        # Update fields directly since we're managing the state in the domain
        if "name" in update_data:
            role_domain.name = update_data["name"]

        if "is_active" in update_data:
            role_domain.is_active = update_data["is_active"]

        if "permission_ids" in update_data:
            role_domain.permission_ids = update_data["permission_ids"]

        if update_data:  # Only update updated_at if there were actual changes
            role_domain.updated_at = datetime.utcnow()

        return role_domain

    @staticmethod
    def update_entity(target: RoleEntity, source: RoleEntity):
        """Apply updated domain Role fields to the entity Role."""
        target.name = source.name
        target.is_active = source.is_active
        target.updated_at = source.updated_at
        target.permission_ids = source.permission_ids or []
