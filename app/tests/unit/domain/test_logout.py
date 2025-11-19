"""Unit tests for logout functionality"""

import pytest
from unittest.mock import AsyncMock, Mock

from app.application.use_cases.auth.logout import LogoutUseCase
from app.domain.entities.refresh_tokens.refresh_token import RefreshToken
from app.domain.services.auth_service import TokenService


class TestLogoutUseCase:
    """Test cases for LogoutUseCase"""

    @pytest.mark.asyncio
    async def test_execute_with_valid_token(self):
        """Test logout with a valid refresh token"""
        # Arrange
        mock_refresh_token_repo = AsyncMock()

        # Create a proper refresh token
        proper_refresh_token = TokenService.create_refresh_token(1)

        # Create a mock refresh token in DB
        mock_db_refresh_token = RefreshToken(
            token=proper_refresh_token, user_id=1, expires_at=Mock(), is_active=True
        )
        mock_refresh_token_repo.get_by_token.return_value = mock_db_refresh_token

        use_case = LogoutUseCase(refresh_token_repository=mock_refresh_token_repo)

        # Act
        result = await use_case.execute(proper_refresh_token)

        # Assert
        assert result is True
        mock_refresh_token_repo.update.assert_called_once()
        updated_token = mock_refresh_token_repo.update.call_args[0][0]
        assert not updated_token.is_active

    @pytest.mark.asyncio
    async def test_execute_with_invalid_token(self):
        """Test logout with an invalid refresh token"""
        # Arrange
        mock_refresh_token_repo = AsyncMock()

        # Return None when searching for token in DB
        mock_refresh_token_repo.get_by_token.return_value = None

        use_case = LogoutUseCase(refresh_token_repository=mock_refresh_token_repo)

        # Act
        result = await use_case.execute("invalid_token")

        # Assert
        assert result is True
        # The repository update should not be called since token was not found
        mock_refresh_token_repo.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_with_none_token(self):
        """Test logout with None token (should succeed)"""
        # Arrange
        mock_refresh_token_repo = AsyncMock()

        use_case = LogoutUseCase(refresh_token_repository=mock_refresh_token_repo)

        # Act
        result = await use_case.execute(None)

        # Assert
        assert result is True
        mock_refresh_token_repo.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_with_empty_token(self):
        """Test logout with empty token string (should succeed)"""
        # Arrange
        mock_refresh_token_repo = AsyncMock()

        use_case = LogoutUseCase(refresh_token_repository=mock_refresh_token_repo)

        # Act
        result = await use_case.execute("")

        # Assert
        assert result is True
        mock_refresh_token_repo.update.assert_not_called()
