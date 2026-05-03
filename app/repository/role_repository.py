"""
Implementation of the role repository using SQLAlchemy.
This is the concrete repository implementation for PostgreSQL database.
"""

from typing import Optional

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.interface.repositories.role_repository_interface import IRoleRepository
from app.domain.entities import RoleEntity
from app.models.role.entity import RoleEntity
from app.models.role.mapper import RoleMapper


class RoleRepository(IRoleRepository):
    """Implementation of role repository operations using SQLAlchemy."""

    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def get_all(self, params: Params) -> Page[RoleEntity]:
        """Get all roles from the repository."""

        query = select(RoleEntity)
        roles_page: Page[RoleEntity] = await paginate(self.session, query, params)

        role_domains = []
        for entity in roles_page.items:
            role_domains.append(RoleMapper.from_entity(entity))

        roles_page.items = role_domains

        return roles_page  # pyright: ignore[reportReturnType]

    async def get_by_id(self, role_id: str) -> Optional[RoleEntity]:
        """Get a role by ID from the repository."""

        role_entity = await self.session.get(RoleEntity, role_id)

        if role_entity is None:
            return None

        return RoleMapper.from_entity(role_entity)

    async def create(self, created_domain: RoleEntity) -> RoleEntity:
        """Create a new role in the repository."""
        role_entity = RoleMapper.to_entity(created_domain)

        self.session.add(role_entity)
        await self.session.commit()
        await self.session.refresh(role_entity)

        return RoleMapper.from_entity(role_entity)

    async def update(self, updated_domain: RoleEntity) -> Optional[RoleEntity]:
        """Update a role in the repository."""
        # First, get the existing role from the database
        existing_role_entity = await self.session.get(RoleEntity, updated_domain.id)

        if not existing_role_entity:
            return None

        # Update the existing entity with the new values
        RoleMapper.update_entity(existing_role_entity, updated_domain)

        await self.session.commit()
        await self.session.refresh(existing_role_entity)

        return RoleMapper.from_entity(existing_role_entity)

    async def delete(self, role_id: str) -> Optional[RoleEntity]:
        """Delete a role from the repository."""
        role_entity = await self.session.get(RoleEntity, role_id)

        if not role_entity:
            return None

        await self.session.delete(role_entity)
        await self.session.commit()

        return RoleMapper.from_entity(role_entity)
