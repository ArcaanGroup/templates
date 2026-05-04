"""
Role Mapper - handles conversion between RoleEntity, RoleEntity, and Role DTO
The Entity is the core of conversions
The Entity gets converted from DTO and Entity
And DTO and Entity gets converted from Entity
No Direct conversions from Entity to DTO or DTO to Entity
"""

from datetime import datetime

from app.domain.entities import RoleEntity
from app.infrastructure.db.orm import RoleORM
from app.interface.dto import Role as RoleDTO
from app.interface.dto import RoleCreate, RoleUpdate


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
    def from_orm(role_orm: RoleORM) -> RoleEntity:
        """Convert entity Role to domain."""
        return RoleEntity(
            id=role_orm.id,
            name=role_orm.name,
            created_at=role_orm.created_at,
            updated_at=role_orm.updated_at,
            is_active=role_orm.is_active,
            permission_ids=role_orm.permission_ids or [],
        )

    @staticmethod
    def to_orm(role_entity: RoleEntity) -> RoleORM:
        """Convert domain Role to entity."""
        entity = RoleORM(
            id=role_entity.id,
            name=role_entity.name,
            created_at=role_entity.created_at,
            updated_at=role_entity.updated_at,
            is_active=role_entity.is_active,
            permission_ids=role_entity.permission_ids or [],
        )
        # Note: The users relationship is handled by SQLAlchemy's ORM when the entity is loaded
        # The many-to-many relationship will be established when the entity is saved to the database
        return entity

    @staticmethod
    def update_from_dto(role_update: RoleUpdate, role_entity: RoleEntity) -> RoleEntity:
        """Apply RoleUpdate DTO to an existing RoleEntity and return updated domain entity."""
        update_data = {
            k: v for k, v in role_update.model_dump().items() if v is not None
        }

        # Update fields directly since we're managing the state in the domain
        if "name" in update_data:
            role_entity.name = update_data["name"]

        if "is_active" in update_data:
            role_entity.is_active = update_data["is_active"]

        if "permission_ids" in update_data:
            role_entity.permission_ids = update_data["permission_ids"]

        if update_data:  # Only update updated_at if there were actual changes
            role_entity.updated_at = datetime.utcnow()

        return role_entity

    @staticmethod
    def update_orm(target: RoleORM, source: RoleEntity):
        """Apply updated Role entity fields to the Role ORM."""
        target.name = source.name
        target.is_active = source.is_active
        target.updated_at = source.updated_at
        target.permission_ids = source.permission_ids or []
