"""
User Mapper - handles conversion between UserEntity, UserEntity, and User DTO
The Entity is the core of conversions
The Entity gets converted from DTO and Entity
And DTO and Entity gets converted from Entity
No Direct conversions from Entity to DTO or DTO to Entity
"""

from sqlalchemy import inspect as sa_inspect

from app.models.role.mapper import RoleMapper
from app.domain.entities import UserEntity
from app.models.user.dto import User as UserDTO
from app.models.user.dto import UserCreate, UserUpdate
from app.models.user.entity import UserEntity


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
    def from_entity(entity_user: UserEntity) -> UserEntity:
        """Convert entity user to domain."""
        # Convert roles from entity to domain
        roles_domain = []

        try:
            # Use SQLAlchemy's inspection to check if the relationship is loaded
            state = sa_inspect(entity_user)
            attr_state = state.attrs["roles"]

            # Check if the relationship attribute is loaded without triggering a load
            if attr_state.loaded_value is not None:
                roles_domain = [
                    RoleMapper.from_entity(role_entity)
                    for role_entity in entity_user.roles
                ]
        # except (AttributeError, KeyError):
        except Exception:
            # If there's any issue accessing roles (e.g., relationship not loaded), return empty list
            roles_domain = []

        return UserEntity(
            id=entity_user.id,
            first_name=entity_user.first_name,
            last_name=entity_user.last_name,
            email=entity_user.email,
            username=entity_user.username,
            hashed_password=entity_user.hashed_password,
            created_at=entity_user.created_at,
            updated_at=entity_user.updated_at,
            is_active=entity_user.is_active,
            roles=roles_domain,
        )

    @staticmethod
    def to_entity(domain_user: UserEntity) -> UserEntity:
        """Convert domain user to entity."""
        entity = UserEntity(
            id=domain_user.id,
            first_name=domain_user.first_name,
            last_name=domain_user.last_name,
            email=domain_user.email,
            username=domain_user.username,
            hashed_password=domain_user.hashed_password,
            created_at=domain_user.created_at,
            updated_at=domain_user.updated_at,
            is_active=domain_user.is_active,
        )
        # Note: The roles relationship is handled by SQLAlchemy's ORM when the entity is loaded
        # The many-to-many relationship will be established when the entity is saved to the database
        return entity

    @staticmethod
    def update_from_dto(user_update: UserUpdate, domain_user: UserEntity) -> UserEntity:
        """Apply UserUpdate DTO to an existing UserEntity and return updated domain entity."""
        # Update only the fields that are provided in the update DTO
        update_data = {
            k: v for k, v in user_update.model_dump().items() if v is not None
        }

        # Apply the updates to the domain user using its update_info method
        domain_user.update_info(
            first_name=update_data.get("first_name"),
            last_name=update_data.get("last_name"),
            email=update_data.get("email"),
            username=update_data.get("username"),
            is_active=update_data.get("is_active"),
        )

        return domain_user

    @staticmethod
    def update_entity(entity: UserEntity, domain: UserEntity):
        entity.first_name = domain.first_name
        entity.last_name = domain.last_name
        entity.email = domain.email
        entity.username = domain.username
        entity.is_active = domain.is_active
        entity.updated_at = domain.updated_at
