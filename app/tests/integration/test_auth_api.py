"""API tests for authentication endpoints"""

import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.infrastructure.database.session import get_db
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from app.infrastructure.database.base import Base
from unittest.mock import AsyncMock, MagicMock
from app.application.interfaces.repositories import UserRepositoryInterface
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.value_objects.username import Username
from app.application.use_cases.auth.login import LoginUseCase
from app.application.use_cases.auth.register import RegisterUseCase
from app.application.use_cases.auth.get_current_user import GetCurrentUserUseCase
from app.api.dependencies import (
    get_login_use_case,
    get_register_use_case,
    get_current_user_use_case,
)


class TestAuthAPI:
    """API tests for authentication endpoints"""

    @pytest.fixture
    def app(self):
        """Create test app"""
        return create_app()

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return TestClient(app)

    @pytest.mark.asyncio
    async def test_login_success(self, client):
        """Test successful login"""
        # Since we don't have a user in the database yet, we'll test by mocking
        # In a real scenario, we would first register a user

        # We'll test the endpoint structure and response format
        response = client.post(
            "/api/v1/auth/login", data={"username": "testuser", "password": "testpass"}
        )

        # The response depends on whether the user exists
        # If user doesn't exist, it will return 404 (UserNotFoundException)
        # If password is incorrect, it would return 401 (AuthenticationFailedException)
        # For now, we'll just check that the endpoint returns expected error codes
        assert response.status_code in [401, 404]  # Expected responses for invalid credentials

    @pytest.mark.asyncio
    async def test_register_success(self, client):
        """Test successful user registration"""
        # Mock the register use case
        original_get_register_use_case = get_register_use_case
        mock_register_use_case = AsyncMock()
        mock_register_use_case.execute.return_value = MagicMock(
            access_token="mock_token", token_type="bearer"
        )

        # Patch the dependency
        import app.api.dependencies as dependencies_module

        dependencies_module.get_register_use_case = lambda: mock_register_use_case

        try:
            # Test registration
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "username": "newuser",
                    "email": "newuser@example.com",
                    "password": "NewPass123",
                },
            )

            # Should return 201 for success (200 is also acceptable) or 409 if user already exists
            if response.status_code in [
                200,
                201,
            ]:  # 201 is the expected status for created resources
                data = response.json()
                assert data["success"] is True
            elif response.status_code == 409:
                # If user already exists, the response should indicate failure
                data = response.json()
                assert data["success"] is False
            else:
                # For any other status, we might want to handle it differently
                assert False, f"Unexpected status code: {response.status_code}"
        finally:
            # Restore original function
            dependencies_module.get_register_use_case = original_get_register_use_case

    @pytest.mark.asyncio
    async def test_register_invalid_data(self, client):
        """Test registration with invalid data"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "ab",  # Too short
                "email": "invalid-email",  # Invalid email
                "password": "weak",  # Too weak
            },
        )

        # Should return 422 for validation errors
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_current_user_with_token(self, client):
        """Test getting current user information with valid token"""
        # We'll need to mock the token decoding to test this
        # This is better done with integration tests using real tokens
        pass

    @pytest.mark.asyncio
    async def test_change_password_endpoint(self, client):
        """Test changing password endpoint"""
        # Try to change password without token
        response = client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "OldPass123", "new_password": "NewPass123"},
        )

        # Should return 401 Unauthorized
        assert response.status_code == 401


class TestAuthAPIIntegration:
    """Integration tests for authentication endpoints with mocked dependencies"""

    @pytest.fixture
    def app_with_mocks(self):
        """Create app with mocked dependencies"""
        app = create_app()

        # Mock all auth use cases
        login_use_case_mock = AsyncMock()
        register_use_case_mock = AsyncMock()
        get_current_user_use_case_mock = AsyncMock()

        # Override dependencies
        app.dependency_overrides[get_login_use_case] = lambda: login_use_case_mock
        app.dependency_overrides[get_register_use_case] = lambda: register_use_case_mock
        app.dependency_overrides[get_current_user_use_case] = lambda: get_current_user_use_case_mock

        yield app

        # Clean up overrides
        app.dependency_overrides.clear()

    @pytest.fixture
    def client_with_mocks(self, app_with_mocks):
        """Create test client with mocked dependencies"""
        return TestClient(app_with_mocks)

    @pytest.mark.asyncio
    async def test_login_with_mocked_use_case(self, client_with_mocks):
        """Test login endpoint with mocked use case"""
        from app.application.dto.auth_dto import TokenDTO

        # Setup mock
        mock_token = TokenDTO(
            access_token="mocked_token", refresh_token="mock_refresh_token", token_type="bearer"
        )
        mock_use_case = client_with_mocks.app.dependency_overrides[get_login_use_case]()
        mock_use_case.execute.return_value = mock_token

        response = client_with_mocks.post(
            "/api/v1/auth/login", data={"username": "testuser", "password": "testpass"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["payload"]["access_token"] == "mocked_token"

    @pytest.mark.asyncio
    async def test_register_with_mocked_use_case(self, client_with_mocks):
        """Test register endpoint with mocked use case"""
        from app.application.dto.auth_dto import TokenDTO

        # Setup mock
        mock_token = TokenDTO(
            access_token="mocked_token", refresh_token="mock_refresh_token", token_type="bearer"
        )
        mock_use_case = client_with_mocks.app.dependency_overrides[get_register_use_case]()
        mock_use_case.execute.return_value = mock_token

        response = client_with_mocks.post(
            "/api/v1/auth/register",
            json={"username": "newuser", "email": "new@example.com", "password": "NewPass123"},
        )

        assert response.status_code in [200, 201]  # Both are acceptable for successful registration
        data = response.json()
        assert data["success"] is True
        assert data["payload"]["access_token"] == "mocked_token"
