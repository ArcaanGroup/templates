"""User repository implementation"""

from typing import Optional, List
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.application.interfaces.repositories import UserRepositoryInterface
from app.domain.entities.user import User
from app.domain.entities.role import Role
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.value_objects.username import Username
from app.domain.value_objects.title import Title
from app.infrastructure.database.models.user import UserModel
from app.infrastructure.database.models.role import RoleModel


class SQLAlchemyUserRepository(UserRepositoryInterface):
    """SQLAlchemy implementation of UserRepository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _to_domain(self, model: UserModel) -> Optional[User]:
        """Convert ORM model to domain entity"""
        if model is None:
            return None

        from app.domain.entities.user import User
        from app.domain.value_objects.email import Email
        from app.domain.value_objects.password import Password
        from app.domain.value_objects.username import Username

        # Convert role models to role entities
        roles = []
        if model.roles:
            for role_model in model.roles:
                import json
                permissions = [uuid.UUID(p) for p in json.loads(role_model.permissions)] if role_model.permissions else []
                from app.domain.value_objects.title import Title
                from app.domain.value_objects.description import Description
                role_entity = Role(
                    id=uuid.UUID(role_model.id),
                    title=Title(role_model.title),
                    description=Description(role_model.description) if role_model.description else None,
                    permissions=permissions
                )
                roles.append(role_entity)

        return User(
            id=model.id,
            username=Username(model.username),
            email=Email(model.email),
            password=Password(model.hashed_password, hashed=model.hashed_password),
            is_active=model.is_active,
            roles=roles,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: User) -> UserModel:
        """Convert domain entity to ORM model"""
        return UserModel(
            id=entity.id,
            username=entity.username.value,
            email=entity.email.value,
            hashed_password=entity.password.hashed,
            is_active=entity.is_active,
        )

    async def create(self, entity: User) -> User:
        """Create a new user"""
        model = self._to_model(entity)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)

        # Assign roles if any
        if entity.roles:
            # Convert domain role entities to model role objects
            role_models = []
            for role in entity.roles:
                # Get the role model from the database based on the role ID
                role_model = await self.session.get(RoleModel, str(role.id))
                if role_model:
                    role_models.append(role_model)

            # Associate the roles with the user
            model.roles = role_models
            await self.session.commit()
            await self.session.refresh(model)

        return await self._to_domain(model)

    async def get_by_id(self, id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.session.execute(
            select(UserModel)
            .options(selectinload(UserModel.roles))
            .where(UserModel.id == id)
        )
        model = result.scalars().first()
        return await self._to_domain(model) if model else None

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        result = await self.session.execute(
            select(UserModel)
            .options(selectinload(UserModel.roles))
            .where(UserModel.username == username)
        )
        model = result.scalars().first()
        return await self._to_domain(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.session.execute(
            select(UserModel)
            .options(selectinload(UserModel.roles))
            .where(UserModel.email == email)
        )
        model = result.scalars().first()
        return await self._to_domain(model) if model else None

    async def get_by_username_or_email(self, identifier: str) -> Optional[User]:
        """Get user by username or email"""
        result = await self.session.execute(
            select(UserModel)
            .options(selectinload(UserModel.roles))
            .where(
                (UserModel.username == identifier) | (UserModel.email == identifier)
            )
        )
        model = result.scalars().first()
        return await self._to_domain(model) if model else None

    async def update(self, entity: User) -> User:
        """Update a user"""
        result = await self.session.execute(
            select(UserModel)
            .options(selectinload(UserModel.roles))
            .where(UserModel.id == entity.id)
        )
        model = result.scalars().first()
        if not model:
            raise ValueError(f"User with id {entity.id} not found")

        model.username = entity.username.value
        model.email = entity.email.value
        model.hashed_password = entity.password.hashed
        model.is_active = entity.is_active

        # Update roles if provided
        if hasattr(entity, '_roles') and entity._roles is not None:
            # Convert domain role entities to model role objects
            role_models = []
            for role in entity._roles:
                # Get the role model from the database based on the role ID
                role_model = await self.session.get(RoleModel, str(role.id))
                if role_model:
                    role_models.append(role_model)

            # Update the user's roles
            model.roles = role_models

        await self.session.commit()
        await self.session.refresh(model)
        return await self._to_domain(model)

    async def delete(self, entity: User) -> None:
        """Delete a user"""
        # First, delete any related refresh tokens to avoid foreign key constraint issues
        from app.infrastructure.database.models.refresh_token import RefreshTokenModel
        from sqlalchemy import delete
        await self.session.execute(delete(RefreshTokenModel).where(RefreshTokenModel.user_id == entity.id))

        # Now delete the user
        result = await self.session.execute(select(UserModel).where(UserModel.id == entity.id))
        model = result.scalars().first()
        if not model:
            raise ValueError(f"User with id {entity.id} not found")

        await self.session.delete(model)
        await self.session.commit()

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """List all users with pagination"""
        result = await self.session.execute(
            select(UserModel)
            .options(selectinload(UserModel.roles))
            .offset(skip)
            .limit(limit)
        )
        models = result.scalars().all()
        return [await self._to_domain(model) for model in models]

    async def count_all(self) -> int:
        """Count all users"""
        from sqlalchemy import func
        result = await self.session.execute(select(func.count(UserModel.id)))
        return result.scalar_one()
