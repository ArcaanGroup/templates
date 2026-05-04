"""
Implementation of the role repository using SQLAlchemy.
This is the concrete repository implementation for PostgreSQL database.
"""

from typing import Optional

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.domain.entities import RoleEntity
from app.infra.db.orm import RoleORM
from app.interface.mappers import RoleMapper
from app.interface.repository.role_repository_interface import IRoleRepository


class RoleRepository(IRoleRepository):
    """Implementation of role repository operations using SQLAlchemy."""

    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def get_all(self, params: Params) -> Page[RoleEntity]:
        """Get all roles from the repository."""

        query = select(RoleORM)
        roles_page: Page[RoleORM] = await paginate(self.session, query, params)

        role_entities = []
        for orm in roles_page.items:
            role_entities.append(RoleMapper.from_orm(orm))

        roles_page.items = role_entities

        return roles_page  # pyright: ignore[reportReturnType]

    async def get_by_id(self, role_id: str) -> Optional[RoleEntity]:
        """Get a role by ID from the repository."""

        role_orm = await self.session.get(RoleORM, role_id)

        if role_orm is None:
            return None

        return RoleMapper.from_orm(role_orm)

    async def create(self, created_domain: RoleEntity) -> RoleEntity:
        """Create a new role in the repository."""
        role_entity = RoleMapper.to_orm(created_domain)

        self.session.add(role_entity)
        await self.session.commit()
        await self.session.refresh(role_entity)

        return RoleMapper.from_orm(role_entity)

    async def update(self, updated_domain: RoleEntity) -> Optional[RoleEntity]:
        """Update a role in the repository."""
        # First, get the existing role from the database
        existing_role_orm = await self.session.get(RoleORM, updated_domain.id)

        if not existing_role_orm:
            return None

        # Update the existing entity with the new values
        RoleMapper.update_orm(existing_role_orm, updated_domain)

        await self.session.commit()
        await self.session.refresh(existing_role_orm)

        return RoleMapper.from_orm(existing_role_orm)

    async def delete(self, role_id: str) -> Optional[RoleEntity]:
        """Delete a role from the repository."""
        role_orm = await self.session.get(RoleORM, role_id)

        if not role_orm:
            return None

        await self.session.delete(role_orm)
        await self.session.commit()

        return RoleMapper.from_orm(role_orm)
