"""Integration tests for authentication repositories"""

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.infrastructure.database.models.user import UserModel
from app.infrastructure.repositories.user_repository import SQLAlchemyUserRepository
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.value_objects.username import Username
from app.infrastructure.database.base import Base


@pytest.fixture
async def db_session():
    """Create a test database session"""
    # Create an in-memory SQLite database for testing
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create async session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
class TestSQLAlchemyUserRepository:
    """Integration tests for SQLAlchemyUserRepository"""

    async def test_create_and_get_user_by_id(self, db_session):
        """Test creating a user and retrieving by ID"""
        # Arrange
        repository = SQLAlchemyUserRepository(db_session)
        user = User(
            username=Username("testuser"),
            email=Email("test@example.com"),
            password=Password("TestPass123"),
        )

        # Act
        created_user = await repository.create(user)

        # Assert
        assert created_user.id is not None
        assert created_user.username.value == "testuser"
        assert created_user.email.value == "test@example.com"
        assert created_user.verify_password("TestPass123")

        # Get by ID
        retrieved_user = await repository.get_by_id(created_user.id)
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.username.value == "testuser"

    async def test_get_user_by_username(self, db_session):
        """Test retrieving user by username"""
        # Arrange
        repository = SQLAlchemyUserRepository(db_session)
        user = User(
            username=Username("testuser"),
            email=Email("test@example.com"),
            password=Password("TestPass123"),
        )
        created_user = await repository.create(user)

        # Act
        retrieved_user = await repository.get_by_username("testuser")

        # Assert
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.username.value == "testuser"

    async def test_get_user_by_email(self, db_session):
        """Test retrieving user by email"""
        # Arrange
        repository = SQLAlchemyUserRepository(db_session)
        user = User(
            username=Username("testuser"),
            email=Email("test@example.com"),
            password=Password("TestPass123"),
        )
        created_user = await repository.create(user)

        # Act
        retrieved_user = await repository.get_by_email("test@example.com")

        # Assert
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email.value == "test@example.com"

    async def test_get_user_by_username_or_email(self, db_session):
        """Test retrieving user by username or email"""
        # Arrange
        repository = SQLAlchemyUserRepository(db_session)
        user = User(
            username=Username("testuser"),
            email=Email("test@example.com"),
            password=Password("TestPass123"),
        )
        created_user = await repository.create(user)

        # Act - Get by username
        retrieved_user = await repository.get_by_username_or_email("testuser")

        # Assert
        assert retrieved_user is not None
        assert retrieved_user.username.value == "testuser"

        # Act - Get by email
        retrieved_user = await repository.get_by_username_or_email("test@example.com")

        # Assert
        assert retrieved_user is not None
        assert retrieved_user.email.value == "test@example.com"

    async def test_update_user(self, db_session):
        """Test updating a user"""
        # Arrange
        repository = SQLAlchemyUserRepository(db_session)
        user = User(
            username=Username("testuser"),
            email=Email("test@example.com"),
            password=Password("TestPass123"),
        )
        created_user = await repository.create(user)

        # Change user details
        new_username = Username("updateduser")
        new_email = Email("updated@example.com")
        new_password = Password("NewTestPass456")
        created_user.update_username(new_username)
        created_user.update_email(new_email)
        created_user.update_password(new_password)

        # Act
        updated_user = await repository.update(created_user)

        # Assert
        assert updated_user.username.value == "updateduser"
        assert updated_user.email.value == "updated@example.com"
        assert updated_user.verify_password("NewTestPass456")

    async def test_delete_user(self, db_session):
        """Test deleting a user"""
        # Arrange
        repository = SQLAlchemyUserRepository(db_session)
        user = User(
            username=Username("testuser"),
            email=Email("test@example.com"),
            password=Password("TestPass123"),
        )
        created_user = await repository.create(user)

        # Act
        await repository.delete(created_user)

        # Assert
        retrieved_user = await repository.get_by_id(created_user.id)
        assert retrieved_user is None

    async def test_user_not_found(self, db_session):
        """Test getting non-existent user"""
        # Arrange
        repository = SQLAlchemyUserRepository(db_session)

        # Act & Assert
        user = await repository.get_by_id(999)
        assert user is None

        user = await repository.get_by_username("nonexistent")
        assert user is None

        user = await repository.get_by_email("nonexistent@example.com")
        assert user is None

        user = await repository.get_by_username_or_email("nonexistent")
        assert user is None
