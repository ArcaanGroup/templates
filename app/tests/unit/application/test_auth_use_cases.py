"""Unit tests for authentication use cases"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.application.use_cases.auth.login import LoginUseCase
from app.application.use_cases.auth.register import RegisterUseCase
from app.application.use_cases.auth.get_current_user import GetCurrentUserUseCase
from app.application.use_cases.auth.change_password import ChangePasswordUseCase
from app.application.dto.auth_dto import LoginDTO, RegisterDTO, UserDTO
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.value_objects.username import Username
from app.domain.exceptions.auth_exceptions import (
    UserNotFoundException,
    AuthenticationFailedException,
    UserAlreadyExistsException,
)


class TestLoginUseCase:
    """Test cases for LoginUseCase"""

    @pytest.mark.asyncio
    async def test_login_success(self):
        """Test successful login"""
        # Arrange
        user_repository = AsyncMock()
        user = User(
            username=Username("testuser"),
            email=Email("test@example.com"),
            password=Password("TestPass123"),
        )
        user_repository.get_by_username.return_value = user

        use_case = LoginUseCase(user_repository)
        dto = LoginDTO(username="testuser", password="TestPass123")

        # Act
        result = await use_case.execute(dto)

        # Assert
        assert result.access_token is not None
        assert result.token_type == "bearer"
        user_repository.get_by_username.assert_called_once_with("testuser")

    @pytest.mark.asyncio
    async def test_login_user_not_found(self):
        """Test login with non-existent user"""
        # Arrange
        user_repository = AsyncMock()
        user_repository.get_by_username.return_value = None

        use_case = LoginUseCase(user_repository)
        dto = LoginDTO(username="nonexistent", password="password")

        # Act & Assert
        with pytest.raises(UserNotFoundException):
            await use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_login_invalid_password(self):
        """Test login with invalid password"""
        # Arrange
        user_repository = AsyncMock()
        user = User(
            username=Username("testuser"),
            email=Email("test@example.com"),
            password=Password("TestPass123"),
        )
        user_repository.get_by_username.return_value = user

        use_case = LoginUseCase(user_repository)
        dto = LoginDTO(username="testuser", password="WrongPass")

        # Act & Assert
        with pytest.raises(AuthenticationFailedException):
            await use_case.execute(dto)


class TestRegisterUseCase:
    """Test cases for RegisterUseCase"""

    @pytest.mark.asyncio
    async def test_register_success(self):
        """Test successful user registration"""
        # Arrange
        user_repository = AsyncMock()
        user_repository.get_by_username.return_value = None
        user_repository.get_by_email.return_value = None

        created_user = User(
            username=Username("newuser"),
            email=Email("new@example.com"),
            password=Password("NewPass123"),
        )
        user_repository.create.return_value = created_user

        use_case = RegisterUseCase(user_repository)
        dto = RegisterDTO(username="newuser", email="new@example.com", password="NewPass123")

        # Act
        result = await use_case.execute(dto)

        # Assert
        assert result.access_token is not None
        assert result.token_type == "bearer"
        user_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_user_already_exists_by_username(self):
        """Test registration when user with username already exists"""
        # Arrange
        user_repository = AsyncMock()
        existing_user = User(
            username=Username("existing"),
            email=Email("existing@example.com"),
            password=Password("ValidPass123"),
        )
        user_repository.get_by_username.return_value = existing_user
        user_repository.get_by_email.return_value = None

        use_case = RegisterUseCase(user_repository)
        dto = RegisterDTO(username="existing", email="new@example.com", password="NewPass123")

        # Act & Assert
        with pytest.raises(UserAlreadyExistsException):
            await use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_register_user_already_exists_by_email(self):
        """Test registration when user with email already exists"""
        # Arrange
        user_repository = AsyncMock()
        user_repository.get_by_username.return_value = None
        existing_user = User(
            username=Username("otheruser"),
            email=Email("existing@example.com"),
            password=Password("ValidPass123"),
        )
        user_repository.get_by_email.return_value = existing_user

        use_case = RegisterUseCase(user_repository)
        dto = RegisterDTO(username="newuser", email="existing@example.com", password="NewPass123")

        # Act & Assert
        with pytest.raises(UserAlreadyExistsException):
            await use_case.execute(dto)


class TestGetCurrentUserUseCase:
    """Test cases for GetCurrentUserUseCase"""

    @pytest.mark.asyncio
    async def test_get_current_user_success(self):
        """Test getting current user info successfully"""
        # Arrange
        user_repository = AsyncMock()
        user = User(
            id=1,
            username=Username("testuser"),
            email=Email("test@example.com"),
            password=Password("TestPass123"),
        )
        user_repository.get_by_username.return_value = user

        use_case = GetCurrentUserUseCase(user_repository)

        # Mock token service to return username
        import app.domain.services.auth_service as auth_service_module

        original_decode = auth_service_module.TokenService.decode_access_token
        auth_service_module.TokenService.decode_access_token = MagicMock(return_value="testuser")

        try:
            # Act
            result = await use_case.execute("mock_token")

            # Assert
            assert isinstance(result, UserDTO)
            assert result.id == 1
            assert result.username == "testuser"
            assert result.email == "test@example.com"
            assert result.is_active is True
        finally:
            # Restore original function
            auth_service_module.TokenService.decode_access_token = original_decode

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token"""
        # Arrange
        user_repository = AsyncMock()
        use_case = GetCurrentUserUseCase(user_repository)

        # Mock token service to return None (invalid token)
        import app.domain.services.auth_service as auth_service_module

        original_decode = auth_service_module.TokenService.decode_access_token
        auth_service_module.TokenService.decode_access_token = MagicMock(return_value=None)

        try:
            # Act & Assert
            with pytest.raises(UserNotFoundException):
                await use_case.execute("invalid_token")
        finally:
            # Restore original function
            auth_service_module.TokenService.decode_access_token = original_decode

    @pytest.mark.asyncio
    async def test_get_current_user_not_found(self):
        """Test getting current user that doesn't exist"""
        # Arrange
        user_repository = AsyncMock()
        user_repository.get_by_username.return_value = None

        use_case = GetCurrentUserUseCase(user_repository)

        # Mock token service to return username
        import app.domain.services.auth_service as auth_service_module

        original_decode = auth_service_module.TokenService.decode_access_token
        auth_service_module.TokenService.decode_access_token = MagicMock(return_value="nonexistent")

        try:
            # Act & Assert
            with pytest.raises(UserNotFoundException):
                await use_case.execute("mock_token")
        finally:
            # Restore original function
            auth_service_module.TokenService.decode_access_token = original_decode


class TestChangePasswordUseCase:
    """Test cases for ChangePasswordUseCase"""

    @pytest.mark.asyncio
    async def test_change_password_success(self):
        """Test successful password change"""
        # Arrange
        user_repository = AsyncMock()
        user = User(
            id=1,
            username=Username("testuser"),
            email=Email("test@example.com"),
            password=Password("OldPass123"),
        )
        user_repository.get_by_id.return_value = user
        user_repository.update.return_value = user

        use_case = ChangePasswordUseCase(user_repository)
        from app.application.dto.auth_dto import PasswordChangeDTO

        dto = PasswordChangeDTO(current_password="OldPass123", new_password="NewPass123")

        # Act
        result = await use_case.execute(1, dto)

        # Assert
        assert result is True
        user_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_change_password_user_not_found(self):
        """Test changing password for non-existent user"""
        # Arrange
        user_repository = AsyncMock()
        user_repository.get_by_id.return_value = None

        use_case = ChangePasswordUseCase(user_repository)
        from app.application.dto.auth_dto import PasswordChangeDTO

        dto = PasswordChangeDTO(current_password="OldPass123", new_password="NewPass123")

        # Act & Assert
        with pytest.raises(AuthenticationFailedException):
            await use_case.execute(999, dto)

    @pytest.mark.asyncio
    async def test_change_password_invalid_current_password(self):
        """Test changing password with invalid current password"""
        # Arrange
        user_repository = AsyncMock()
        user = User(
            id=1,
            username=Username("testuser"),
            email=Email("test@example.com"),
            password=Password("OldPass123"),
        )
        user_repository.get_by_id.return_value = user

        use_case = ChangePasswordUseCase(user_repository)
        from app.application.dto.auth_dto import PasswordChangeDTO

        dto = PasswordChangeDTO(current_password="WrongPass", new_password="NewPass123")

        # Act & Assert
        with pytest.raises(AuthenticationFailedException):
            await use_case.execute(1, dto)
