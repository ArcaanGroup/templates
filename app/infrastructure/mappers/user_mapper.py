"""
User Mapper - handles conversion between UserEntity, UserEntity, and User DTO
The Entity is the core of conversions
The Entity gets converted from DTO and Entity
And DTO and Entity gets converted from Entity
No Direct conversions from Entity to DTO or DTO to Entity
"""

from sqlalchemy import inspect as sa_inspect

from app.domain.entities import UserEntity
from app.infrastructure.mappers import RoleMapper
from app.infrastructure.orm import UserORM
from app.interface.dto import User as UserDTO
from app.interface.dto import UserCreate, UserUpdate


class UserMapper:
    """Mapper class to handle conversions between user representations."""

    @staticmethod
    def from_dto(dto: UserCreate) -> UserEntity:
        """Convert DTO user to domain."""
        return UserEntity.create(
            first_name=dto.first_name,
            last_name=dto.last_name,
            email=dto.email,
            username=dto.username,
            password=dto.password,
        )

    @staticmethod
    def to_dto(domain_user: UserEntity) -> UserDTO:
        """Convert domain user to DTO."""
        # Convert roles from domain to DTO
        roles_dto = []
        if domain_user.roles:
            roles_dto = [RoleMapper.to_dto(role) for role in domain_user.roles]

        return UserDTO(
            id=domain_user.id,
            first_name=domain_user.first_name,
            last_name=domain_user.last_name,
            email=domain_user.email,
            username=domain_user.username,
            roles=roles_dto,
            created_at=domain_user.created_at,
            updated_at=domain_user.updated_at,
            is_active=domain_user.is_active,
        )

    @staticmethod
    def from_orm(user_orm: UserORM) -> UserEntity:
        """Convert entity user to domain."""
        # Convert roles from entity to domain
        roles_domain = []

        try:
            # Use SQLAlchemy's inspection to check if the relationship is loaded
            state = sa_inspect(user_orm)
            attr_state = state.attrs["roles"]

            # Check if the relationship attribute is loaded without triggering a load
            if attr_state.loaded_value is not None:
                roles_domain = [
                    RoleMapper.from_orm(role_entity) for role_entity in user_orm.roles
                ]
        # except (AttributeError, KeyError):
        except Exception:
            # If there's any issue accessing roles (e.g., relationship not loaded), return empty list
            roles_domain = []

        return UserEntity(
            id=user_orm.id,
            first_name=user_orm.first_name,
            last_name=user_orm.last_name,
            email=user_orm.email,
            username=user_orm.username,
            hashed_password=user_orm.hashed_password,
            created_at=user_orm.created_at,
            updated_at=user_orm.updated_at,
            is_active=user_orm.is_active,
            roles=roles_domain,
        )

    @staticmethod
    def to_orm(user_entity: UserEntity) -> UserORM:
        """Convert domain user to entity."""
        orm = UserORM(
            id=user_entity.id,
            first_name=user_entity.first_name,
            last_name=user_entity.last_name,
            email=user_entity.email,
            username=user_entity.username,
            hashed_password=user_entity.hashed_password,
            created_at=user_entity.created_at,
            updated_at=user_entity.updated_at,
            is_active=user_entity.is_active,
        )
        # Note: The roles relationship is handled by SQLAlchemy's ORM when the entity is loaded
        # The many-to-many relationship will be established when the entity is saved to the database
        return orm

    @staticmethod
    def update_from_dto(user_update: UserUpdate, user_entity: UserEntity) -> UserEntity:
        """Apply UserUpdate DTO to an existing UserEntity and return updated entity."""
        # Update only the fields that are provided in the update DTO
        update_data = {
            k: v for k, v in user_update.model_dump().items() if v is not None
        }

        # Apply the updates to the domain user using its update_info method
        user_entity.update_info(
            first_name=update_data.get("first_name"),
            last_name=update_data.get("last_name"),
            email=update_data.get("email"),
            username=update_data.get("username"),
            is_active=update_data.get("is_active"),
        )

        return user_entity

    @staticmethod
    def update_orm(orm: UserORM, entity: UserEntity):
        orm.first_name = entity.first_name
        orm.last_name = entity.last_name
        orm.email = entity.email
        orm.username = entity.username
        orm.is_active = entity.is_active
        orm.updated_at = entity.updated_at
