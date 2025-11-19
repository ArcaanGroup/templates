"""Unit tests for refresh token functionality"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

from app.application.dto.auth_dto import RefreshTokenDTO, TokenDTO
from app.application.use_cases.auth.refresh_token import RefreshTokenUseCase
from app.domain.entities.refresh_tokens.refresh_token import RefreshToken
from app.domain.exceptions.auth_exceptions import AuthenticationFailedException
from app.domain.services.auth_service import TokenService


class TestRefreshTokenUseCase:
    """Test cases for RefreshTokenUseCase"""

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test successful token refresh"""
        # Arrange
        mock_refresh_token_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        # Create a proper refresh token
        proper_refresh_token = TokenService.create_refresh_token(1)

        # Create a mock refresh token in DB that is valid (with the same token string)
        mock_db_refresh_token = RefreshToken(
            token=proper_refresh_token,
            user_id=1,
            expires_at=datetime.utcnow() + timedelta(days=1),
            is_active=True,
        )
        mock_refresh_token_repo.get_by_token.return_value = mock_db_refresh_token

        # Create a mock user
        mock_user = Mock()
        mock_user.id = 1
        mock_user.is_active = True
        mock_user.username.value = "testuser"
        mock_user_repo.get_by_id.return_value = mock_user

        use_case = RefreshTokenUseCase(
            refresh_token_repository=mock_refresh_token_repo, user_repository=mock_user_repo
        )

        dto = RefreshTokenDTO(refresh_token=proper_refresh_token)

        # Act
        result = await use_case.execute(dto)

        # Assert
        assert isinstance(result, TokenDTO)
        assert result.access_token
        assert result.refresh_token
        assert result.token_type == "bearer"

        # Verify that old token was deactivated
        mock_refresh_token_repo.update.assert_called_once()
        updated_token = mock_refresh_token_repo.update.call_args[0][0]
        assert not updated_token.is_active

    @pytest.mark.asyncio
    async def test_execute_invalid_refresh_token(self):
        """Test refresh with invalid token"""
        # Arrange
        mock_refresh_token_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        use_case = RefreshTokenUseCase(
            refresh_token_repository=mock_refresh_token_repo, user_repository=mock_user_repo
        )

        # Use an invalid token string that can't be decoded
        dto = RefreshTokenDTO(refresh_token="invalid_token")

        # Act & Assert
        with pytest.raises(AuthenticationFailedException):
            await use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_execute_refresh_token_not_found_in_db(self):
        """Test refresh when token not found in database"""
        # Arrange
        mock_refresh_token_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        # Return None when searching for token in DB
        mock_refresh_token_repo.get_by_token.return_value = None

        use_case = RefreshTokenUseCase(
            refresh_token_repository=mock_refresh_token_repo, user_repository=mock_user_repo
        )

        # Create a valid token for the purpose of this test (decode will succeed)
        valid_token = TokenService.create_refresh_token(1)
        dto = RefreshTokenDTO(refresh_token=valid_token)

        # Act & Assert
        with pytest.raises(AuthenticationFailedException):
            await use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_execute_inactive_refresh_token(self):
        """Test refresh with inactive token in database"""
        # Arrange
        mock_refresh_token_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        # Create a mock inactive refresh token in DB
        mock_db_refresh_token = RefreshToken(
            token="refresh_token_123",
            user_id=1,
            expires_at=datetime.utcnow() + timedelta(days=1),
            is_active=False,  # Inactive token
        )
        mock_refresh_token_repo.get_by_token.return_value = mock_db_refresh_token

        use_case = RefreshTokenUseCase(
            refresh_token_repository=mock_refresh_token_repo, user_repository=mock_user_repo
        )

        # Create a valid token for the purpose of this test (decode will succeed)
        valid_token = TokenService.create_refresh_token(1)
        dto = RefreshTokenDTO(refresh_token=valid_token)

        # Act & Assert
        with pytest.raises(AuthenticationFailedException):
            await use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_execute_expired_refresh_token(self):
        """Test refresh with expired token"""
        # Arrange
        mock_refresh_token_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        # Create a mock expired refresh token in DB
        mock_db_refresh_token = RefreshToken(
            token="refresh_token_123",
            user_id=1,
            expires_at=datetime.utcnow() - timedelta(days=1),  # Expired
            is_active=True,
        )
        mock_refresh_token_repo.get_by_token.return_value = mock_db_refresh_token

        use_case = RefreshTokenUseCase(
            refresh_token_repository=mock_refresh_token_repo, user_repository=mock_user_repo
        )

        # Create a valid token for the purpose of this test (decode will succeed)
        valid_token = TokenService.create_refresh_token(1)
        dto = RefreshTokenDTO(refresh_token=valid_token)

        # Act & Assert
        with pytest.raises(AuthenticationFailedException):
            await use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_execute_user_not_found(self):
        """Test refresh when user not found"""
        # Arrange
        mock_refresh_token_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        # Create a mock refresh token in DB that is valid
        mock_db_refresh_token = RefreshToken(
            token="refresh_token_123",
            user_id=1,
            expires_at=datetime.utcnow() + timedelta(days=1),
            is_active=True,
        )
        mock_refresh_token_repo.get_by_token.return_value = mock_db_refresh_token

        # Return None when searching for user
        mock_user_repo.get_by_id.return_value = None

        use_case = RefreshTokenUseCase(
            refresh_token_repository=mock_refresh_token_repo, user_repository=mock_user_repo
        )

        # Create a valid token for the purpose of this test (decode will succeed)
        valid_token = TokenService.create_refresh_token(1)
        dto = RefreshTokenDTO(refresh_token=valid_token)

        # Act & Assert
        with pytest.raises(AuthenticationFailedException):
            await use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_execute_user_deactivated(self):
        """Test refresh when user is deactivated"""
        # Arrange
        mock_refresh_token_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        # Create a mock refresh token in DB that is valid
        mock_db_refresh_token = RefreshToken(
            token="refresh_token_123",
            user_id=1,
            expires_at=datetime.utcnow() + timedelta(days=1),
            is_active=True,
        )
        mock_refresh_token_repo.get_by_token.return_value = mock_db_refresh_token

        # Create a mock deactivated user
        mock_user = Mock()
        mock_user.id = 1
        mock_user.is_active = False  # Deactivated
        mock_user_repo.get_by_id.return_value = mock_user

        use_case = RefreshTokenUseCase(
            refresh_token_repository=mock_refresh_token_repo, user_repository=mock_user_repo
        )

        # Create a valid token for the purpose of this test (decode will succeed)
        valid_token = TokenService.create_refresh_token(1)
        dto = RefreshTokenDTO(refresh_token=valid_token)

        # Act & Assert
        with pytest.raises(AuthenticationFailedException):
            await use_case.execute(dto)

    @pytest.mark.asyncio
    async def test_execute_mismatched_user_id(self):
        """Test refresh when token user ID doesn't match DB token user ID"""
        # Arrange
        mock_refresh_token_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        # Create a mock refresh token in DB with user_id = 2
        mock_db_refresh_token = RefreshToken(
            token="refresh_token_123",
            user_id=2,  # Different user ID
            expires_at=datetime.utcnow() + timedelta(days=1),
            is_active=True,
        )
        mock_refresh_token_repo.get_by_token.return_value = mock_db_refresh_token

        use_case = RefreshTokenUseCase(
            refresh_token_repository=mock_refresh_token_repo, user_repository=mock_user_repo
        )

        # Create a token for user_id = 1 (will decode to user_id 1)
        valid_token = TokenService.create_refresh_token(1)
        dto = RefreshTokenDTO(refresh_token=valid_token)

        # Act & Assert
        with pytest.raises(AuthenticationFailedException):
            await use_case.execute(dto)
