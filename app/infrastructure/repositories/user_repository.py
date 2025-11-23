"""User repository implementation"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.application.interfaces.repositories import UserRepositoryInterface
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.value_objects.username import Username
from app.infrastructure.database.models.user import UserModel


class SQLAlchemyUserRepository(UserRepositoryInterface):
    """SQLAlchemy implementation of UserRepository"""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: UserModel) -> User:
        """Convert ORM model to domain entity"""
        from app.domain.entities.user import User
        from app.domain.value_objects.email import Email
        from app.domain.value_objects.password import Password
        from app.domain.value_objects.username import Username

        return User(
            id=model.id,
            username=Username(model.username),
            email=Email(model.email),
            password=Password(model.hashed_password, hashed=model.hashed_password),
            is_active=model.is_active,
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
        return self._to_domain(model)

    async def get_by_id(self, id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.session.execute(select(UserModel).where(UserModel.id == id))
        model = result.scalars().first()
        return self._to_domain(model) if model else None

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        result = await self.session.execute(select(UserModel).where(UserModel.username == username))
        model = result.scalars().first()
        return self._to_domain(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.session.execute(select(UserModel).where(UserModel.email == email))
        model = result.scalars().first()
        return self._to_domain(model) if model else None

    async def get_by_username_or_email(self, identifier: str) -> Optional[User]:
        """Get user by username or email"""
        result = await self.session.execute(
            select(UserModel).where(
                (UserModel.username == identifier) | (UserModel.email == identifier)
            )
        )
        model = result.scalars().first()
        return self._to_domain(model) if model else None

    async def update(self, entity: User) -> User:
        """Update a user"""
        result = await self.session.execute(select(UserModel).where(UserModel.id == entity.id))
        model = result.scalars().first()
        if not model:
            raise ValueError(f"User with id {entity.id} not found")

        model.username = entity.username.value
        model.email = entity.email.value
        model.hashed_password = entity.password.hashed
        model.is_active = entity.is_active

        await self.session.commit()
        await self.session.refresh(model)
        return self._to_domain(model)

    async def delete(self, entity: User) -> None:
        """Delete a user"""
        result = await self.session.execute(select(UserModel).where(UserModel.id == entity.id))
        model = result.scalars().first()
        if not model:
            raise ValueError(f"User with id {entity.id} not found")

        await self.session.delete(model)
        await self.session.commit()

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """List all users with pagination"""
        result = await self.session.execute(
            select(UserModel).offset(skip).limit(limit)
        )
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def count_all(self) -> int:
        """Count all users"""
        from sqlalchemy import func
        result = await self.session.execute(select(func.count(UserModel.id)))
        return result.scalar_one()
