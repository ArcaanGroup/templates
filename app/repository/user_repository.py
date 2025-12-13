"""
Implementation of the user repository using SQLAlchemy.
This is the concrete repository implementation for PostgreSQL database.
"""

from typing import List, Optional

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.error.exceptions import ConflictException, ResourceNotFoundException
from app.interface.repositories.user_repository_interface import IUserRepository
from app.models.role import (
    UserRolesAssociation,
)
from app.models.role.entity import RoleEntity
from app.models.user.domain import UserDomain
from app.models.user.entity import UserEntity
from app.models.user.mapper import UserMapper


class UserRepository(IUserRepository):
    """Implementation of user repository operations using SQLAlchemy."""

    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def create(self, user_to_create: UserDomain) -> UserDomain:
        """Create a new user in the repository."""
        # Convert domain entity to database entity for persistence
        user_entity = UserMapper.to_entity(user_to_create)

        self.session.add(user_entity)
        await self.session.commit()

        # Refresh the entity to ensure it has the auto-generated fields (like ID)
        # Get the user back with all relationships to prevent detached instance errors
        result = await self.session.execute(
            select(UserEntity)
            .options(selectinload(UserEntity.roles))
            .where(UserEntity.id == user_entity.id)
        )
        refreshed_user_entity = result.scalar_one_or_none()

        # Convert back to domain entity for return
        return UserMapper.from_entity(refreshed_user_entity)

    async def get_by_id(self, user_id: str) -> Optional[UserDomain]:
        """Get a user by ID from the repository."""
        result = await self.session.execute(
            select(UserEntity)
            .options(selectinload(UserEntity.roles))
            .where(UserEntity.id == user_id)
        )
        user_in_db = result.scalar_one_or_none()

        if user_in_db is None:
            return None

        return UserMapper.from_entity(user_in_db)

    async def get_all(self, params: Params) -> Page[UserDomain]:
        """Get all users from the repository."""
        query = select(UserEntity).options(selectinload(UserEntity.roles))
        users_page: Page[UserEntity] = await paginate(self.session, query, params)

        user_domains: List[UserDomain] = []
        for user in users_page.items:
            domain = UserMapper.from_entity(user)
            user_domains.append(domain)

        users_page.items = user_domains  # pyright: ignore[reportAttributeAccessIssue]

        return users_page  # pyright: ignore[reportReturnType]

    async def update(self, source: UserDomain) -> Optional[UserDomain]:
        """Update a user in the repository."""
        user_entity = await self.session.get(UserEntity, source.id)

        if not user_entity:
            return None

        UserMapper.update_entity(user_entity, source)

        await self.session.commit()
        await self.session.refresh(user_entity)

        return UserMapper.from_entity(user_entity)

    async def delete(self, user_id: str) -> UserDomain:
        """Delete a user from the repository."""
        # Get the user to check if it exists
        result = await self.session.execute(
            select(UserEntity)
            .options(selectinload(UserEntity.roles))
            .where(UserEntity.id == user_id)
        )
        target = result.scalar_one_or_none()

        if not target:
            raise ResourceNotFoundException(resource_type="User", identifier=user_id)

        # Delete the user
        await self.session.delete(target)
        await self.session.commit()

        return UserMapper.from_entity(target)

    async def get_by_email(self, email: str) -> Optional[UserDomain]:
        """Get a user by email from the repository."""
        result = await self.session.execute(
            select(UserEntity)
            .options(selectinload(UserEntity.roles))
            .where(UserEntity.email == email)
        )
        target = result.scalar_one_or_none()

        if not target:
            return None

        return UserMapper.from_entity(target)

    async def get_by_username(self, username: str) -> Optional[UserDomain]:
        """Get a user by username from the repository."""
        result = await self.session.execute(
            select(UserEntity)
            .options(selectinload(UserEntity.roles))
            .where(UserEntity.username == username)
        )
        target = result.scalar_one_or_none()

        if not target:
            return None

        return UserMapper.from_entity(target)

    async def assign_role(self, user_id: str, role_id: str) -> UserDomain:
        """Assign a role to a user."""

        result_user = await self.session.execute(
            select(UserEntity)
            .options(selectinload(UserEntity.roles))
            .where(UserEntity.id == user_id)
        )
        target_user = result_user.scalar_one_or_none()
        if not target_user:
            raise ResourceNotFoundException(resource_type="User", identifier=user_id)

        result_role = await self.session.execute(
            select(RoleEntity).where(RoleEntity.id == role_id)
        )
        target_role = result_role.scalar_one_or_none()
        if not target_role:
            raise ResourceNotFoundException(resource_type="Role", identifier=role_id)

        # Check if the relationship already exists
        existing_assoc = await self.session.execute(
            select(UserRolesAssociation).where(
                UserRolesAssociation.c.user_id == user_id,
                UserRolesAssociation.c.role_id == role_id,
            )
        )

        if existing_assoc.fetchone():
            # Relationship already exists, return current user
            raise ConflictException("User already has this role")

        # Add the relationship
        await self.session.execute(
            UserRolesAssociation.insert().values(user_id=user_id, role_id=role_id)
        )
        await self.session.commit()
        await self.session.refresh(target_user)

        return UserMapper.from_entity(target_user)

    async def remove_role(self, user_id: str, role_id: str) -> UserDomain:
        """Remove a role from a user."""

        result = await self.session.execute(
            select(UserEntity).where(UserEntity.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise ResourceNotFoundException(resource_type="User", identifier=user_id)

        # Remove the relationship
        await self.session.execute(
            UserRolesAssociation.delete().where(
                UserRolesAssociation.c.user_id == user_id,
                UserRolesAssociation.c.role_id == role_id,
            )
        )
        await self.session.commit()

        # Refresh the user to get updated roles
        await self.session.refresh(user)

        result = await self.session.execute(
            select(UserEntity)
            .options(selectinload(UserEntity.roles))
            .where(UserEntity.id == user_id)
        )
        user = result.scalar_one_or_none()

        return UserMapper.from_entity(user)
