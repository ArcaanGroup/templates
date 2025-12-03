"""SQLAlchemy role repository implementation"""

from typing import List, Optional
import json
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.repositories import RoleRepositoryInterface
from app.domain.entities.role import Role
from app.infrastructure.database.models.role import RoleModel


class SQLAlchemyRoleRepository(RoleRepositoryInterface):
    """SQLAlchemy implementation of role repository"""

    def __init__(self, db_session: AsyncSession):
        self._db_session = db_session

    async def create(self, role: Role) -> Role:
        """Create a new role"""
        # Serialize permissions to JSON string
        permissions_json = json.dumps([str(p) for p in role._permissions])

        # Convert the role ID to string to ensure compatibility with database
        role_model = RoleModel(
            id=str(role.id),  # Convert UUID to string
            title=role._title,
            description=role._description,
            permissions=permissions_json,
            created_at=role.created_at,
            updated_at=role.updated_at
        )
        self._db_session.add(role_model)
        await self._db_session.commit()
        await self._db_session.refresh(role_model)

        # Map back to domain entity, deserializing permissions
        permissions = [uuid.UUID(p) for p in json.loads(role_model.permissions)]
        return Role(
            id=uuid.UUID(role_model.id),  # Convert string back to UUID
            title=role_model.title,
            description=role_model.description,
            permissions=permissions,
            created_at=role_model.created_at,
            updated_at=role_model.updated_at
        )

    async def get_by_id(self, role_id: uuid.UUID) -> Optional[Role]:
        """Get role by ID"""
        stmt = select(RoleModel).where(RoleModel.id == str(role_id))  # Convert UUID to string for query
        result = await self._db_session.execute(stmt)
        role_model = result.scalar_one_or_none()

        if not role_model:
            return None

        # Deserialize permissions from JSON string
        permissions = [uuid.UUID(p) for p in json.loads(role_model.permissions)]
        return Role(
            id=uuid.UUID(role_model.id),  # Convert string back to UUID
            title=role_model.title,
            description=role_model.description,
            permissions=permissions,
            created_at=role_model.created_at,
            updated_at=role_model.updated_at
        )

    async def get_by_title(self, title: str) -> Optional[Role]:
        """Get role by title"""
        stmt = select(RoleModel).where(RoleModel.title == title)
        result = await self._db_session.execute(stmt)
        role_model = result.scalar_one_or_none()

        if not role_model:
            return None

        # Deserialize permissions from JSON string
        permissions = [uuid.UUID(p) for p in json.loads(role_model.permissions)]
        return Role(
            id=uuid.UUID(role_model.id),  # Convert string back to UUID
            title=role_model.title,
            description=role_model.description,
            permissions=permissions,
            created_at=role_model.created_at,
            updated_at=role_model.updated_at
        )

    async def list_all(self) -> List[Role]:
        """List all roles"""
        stmt = select(RoleModel)
        result = await self._db_session.execute(stmt)
        role_models = result.scalars().all()

        return [
            Role(
                id=uuid.UUID(role_model.id),  # Convert string back to UUID
                title=role_model.title,
                description=role_model.description,
                permissions=[uuid.UUID(p) for p in json.loads(role_model.permissions)],
                created_at=role_model.created_at,
                updated_at=role_model.updated_at
            )
            for role_model in role_models
        ]

    async def update(self, role: Role) -> Role:
        """Update an existing role"""
        stmt = select(RoleModel).where(RoleModel.id == str(role.id))  # Convert UUID to string for query
        result = await self._db_session.execute(stmt)
        role_model = result.scalar_one_or_none()

        if not role_model:
            raise ValueError(f"Role with ID {role.id} not found")

        role_model.title = role._title
        role_model.description = role._description
        # Serialize permissions to JSON string
        role_model.permissions = json.dumps([str(p) for p in role._permissions])
        role_model.updated_at = role.updated_at

        await self._db_session.commit()
        await self._db_session.refresh(role_model)

        # Deserialize permissions from JSON string
        permissions = [uuid.UUID(p) for p in json.loads(role_model.permissions)]
        return Role(
            id=uuid.UUID(role_model.id),  # Convert string back to UUID
            title=role_model.title,
            description=role_model.description,
            permissions=permissions,
            created_at=role_model.created_at,
            updated_at=role_model.updated_at
        )

    async def delete(self, role_id: uuid.UUID) -> bool:
        """Delete a role by ID"""
        stmt = select(RoleModel).where(RoleModel.id == str(role_id))  # Convert UUID to string for query
        result = await self._db_session.execute(stmt)
        role_model = result.scalar_one_or_none()

        if not role_model:
            return False

        await self._db_session.delete(role_model)
        await self._db_session.commit()
        return True

    async def get_user_roles(self, user_id: int) -> List[Role]:
        """Get all roles for a specific user"""
        # Query to get roles for a specific user via the user_roles association table
        stmt = (
            select(RoleModel)
            .join(RoleModel.users)
            .where(RoleModel.users.any(id=user_id))
        )
        result = await self._db_session.execute(stmt)
        role_models = result.scalars().all()

        return [
            Role(
                id=uuid.UUID(role_model.id),  # Convert string back to UUID
                title=role_model.title,
                description=role_model.description,
                permissions=[uuid.UUID(p) for p in json.loads(role_model.permissions)],
                created_at=role_model.created_at,
                updated_at=role_model.updated_at
            )
            for role_model in role_models
        ]

    # Method to get user roles directly as RoleModel
    async def get_user_roles_model(self, user_id: int) -> List[RoleModel]:
        """Get all roles for a specific user as RoleModel instances"""
        # Query to get roles for a specific user via the user_roles association table
        stmt = (
            select(RoleModel)
            .join(RoleModel.users)
            .where(RoleModel.users.any(id=user_id))
        )
        result = await self._db_session.execute(stmt)
        return result.scalars().all()

    # Method to get role by title as RoleModel
    async def get_role_model_by_title(self, title: str) -> Optional[RoleModel]:
        """Get role by title as RoleModel"""
        stmt = select(RoleModel).where(RoleModel.title == title)
        result = await self._db_session.execute(stmt)
        return result.scalar_one_or_none()
