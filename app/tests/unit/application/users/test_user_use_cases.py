"""Unit tests for User use cases"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.application.dto.auth_dto import UserCreateDTO, UserUpdateDTO
from app.application.interfaces.event_bus import EventBusInterface
from app.application.interfaces.cache import CacheInterface
from app.application.interfaces.repositories import UserRepositoryInterface
from app.application.use_cases.users.create_user import CreateUserUseCase
from app.application.use_cases.users.get_user import GetUserUseCase
from app.application.use_cases.users.list_users import ListUsersUseCase
from app.application.use_cases.users.update_user import UpdateUserUseCase
from app.application.use_cases.users.delete_user import DeleteUserUseCase
from app.domain.exceptions.auth_exceptions import UserNotFoundException, UserAlreadyExistsException
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.value_objects.username import Username
from fastapi_pagination import Params


@pytest.fixture
def mock_repository():
    return AsyncMock(spec=UserRepositoryInterface)


@pytest.fixture
def mock_cache():
    return AsyncMock(spec=CacheInterface)


@pytest.fixture
def mock_event_bus():
    return AsyncMock(spec=EventBusInterface)


@pytest.fixture
def create_user_use_case(mock_repository, mock_event_bus):
    return CreateUserUseCase(mock_repository, mock_event_bus)


@pytest.fixture
def get_user_use_case(mock_repository, mock_cache):
    return GetUserUseCase(mock_repository, mock_cache)


@pytest.fixture
def list_users_use_case(mock_repository):
    return ListUsersUseCase(mock_repository)


@pytest.fixture
def update_user_use_case(mock_repository, mock_cache):
    return UpdateUserUseCase(mock_repository, mock_cache)


@pytest.fixture
def delete_user_use_case(mock_repository, mock_cache):
    return DeleteUserUseCase(mock_repository, mock_cache)


@pytest.fixture
def sample_user():
    return User(
        id=1,
        username=Username("testuser"),
        email=Email("test@example.com"),
        password=Password("SecurePass123"),
    )


class TestCreateUserUseCase:
    """Test cases for CreateUserUseCase"""

    async def test_execute_success(self, create_user_use_case, mock_repository, mock_event_bus, sample_user):
        """Test successful user creation"""
        # Arrange
        dto = UserCreateDTO(
            username="testuser",
            email="test@example.com",
            password="SecurePass123",
            is_active=True
        )
        mock_repository.get_by_username.return_value = None
        mock_repository.get_by_email.return_value = None
        mock_repository.create.return_value = sample_user

        # Act
        result = await create_user_use_case.execute(dto)

        # Assert
        assert result.id == 1
        assert result.username == "testuser"
        assert result.email == "test@example.com"
        assert result.is_active is True
        mock_repository.create.assert_called_once()
        mock_event_bus.publish.assert_called()

    async def test_execute_user_already_exists(self, create_user_use_case, mock_repository):
        """Test creating a user that already exists"""
        # Arrange
        dto = UserCreateDTO(
            username="existinguser",
            email="existing@example.com",
            password="SecurePass123",
            is_active=True
        )
        existing_user = MagicMock()
        mock_repository.get_by_username_or_email.return_value = existing_user

        # Act & Assert
        with pytest.raises(UserAlreadyExistsException):
            await create_user_use_case.execute(dto)


class TestGetUserUseCase:
    """Test cases for GetUserUseCase"""

    async def test_execute_success(self, get_user_use_case, mock_repository, mock_cache, sample_user):
        """Test successful user retrieval"""
        # Arrange
        mock_cache.get.return_value = None  # Not in cache
        mock_repository.get_by_id.return_value = sample_user

        # Act
        result = await get_user_use_case.execute(1)

        # Assert
        assert result.id == 1
        assert result.username == "testuser"
        mock_repository.get_by_id.assert_called_once_with(1)
        mock_cache.set.assert_called_once()

    async def test_execute_user_not_found(self, get_user_use_case, mock_repository, mock_cache):
        """Test retrieval of non-existent user"""
        # Arrange
        mock_cache.get.return_value = None  # Not in cache
        mock_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(UserNotFoundException):
            await get_user_use_case.execute(999)


class TestListUsersUseCase:
    """Test cases for ListUsersUseCase"""

    async def test_execute_success(self, list_users_use_case, mock_repository, sample_user):
        """Test successful users listing"""
        # Arrange
        mock_repository.list_all.return_value = [sample_user]
        mock_repository.count_all.return_value = 1
        params = Params()

        # Act
        result = await list_users_use_case.execute(params)

        # Assert
        assert len(result.items) == 1
        assert result.items[0].id == 1
        assert result.total == 1
        assert result.page == 1


class TestUpdateUserUseCase:
    """Test cases for UpdateUserUseCase"""

    async def test_execute_success(self, update_user_use_case, mock_repository, mock_cache, sample_user):
        """Test successful user update"""
        # Arrange
        dto = UserUpdateDTO(username="updateduser", email="updated@example.com", is_active=False)
        mock_repository.get_by_id.return_value = sample_user
        mock_repository.update.return_value = sample_user

        # Act
        result = await update_user_use_case.execute(1, dto)

        # Assert
        assert result.username == "updateduser"
        assert result.email == "updated@example.com"
        assert result.is_active is False
        mock_repository.update.assert_called_once()
        mock_cache.delete.assert_called_once_with("user:1")

    async def test_execute_user_not_found(self, update_user_use_case, mock_repository):
        """Test updating non-existent user"""
        # Arrange
        dto = UserUpdateDTO(username="updateduser")
        mock_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(UserNotFoundException):
            await update_user_use_case.execute(999, dto)


class TestDeleteUserUseCase:
    """Test cases for DeleteUserUseCase"""

    async def test_execute_success(self, delete_user_use_case, mock_repository, mock_cache, sample_user):
        """Test successful user deletion"""
        # Arrange
        mock_repository.get_by_id.return_value = sample_user

        # Act
        await delete_user_use_case.execute(1)

        # Assert
        mock_repository.delete.assert_called_once_with(sample_user)
        mock_cache.delete.assert_called_once_with("user:1")

    async def test_execute_user_not_found(self, delete_user_use_case, mock_repository):
        """Test deleting non-existent user"""
        # Arrange
        mock_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(UserNotFoundException):
            await delete_user_use_case.execute(999)
