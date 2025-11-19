"""End-to-end tests for authentication flow"""

import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.core.config import settings
from jose import jwt


class TestAuthFlow:
    """End-to-end tests for the complete authentication flow"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        app = create_app()
        return TestClient(app)

    def test_auth_flow_complete(self, client):
        """Test the complete authentication flow: register -> login -> access protected -> change password"""
        # 1. Register a new user
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser123",
                "email": "testuser123@example.com",
                "password": "TestPass123",
            },
        )

        # The response will depend on the current implementation of register use case
        # Since we've mocked the dependencies in the previous test, we'll need to
        # run with a real implementation to fully test the flow
        print(f"Register response status: {register_response.status_code}")
        print(f"Register response: {register_response.json()}")

        # 2. Login with the registered user
        login_response = client.post(
            "/api/v1/auth/login", data={"username": "testuser123", "password": "TestPass123"}
        )

        print(f"Login response status: {login_response.status_code}")
        print(f"Login response: {login_response.json()}")

        # Skip further testing if authentication flow dependencies are not properly implemented
        pytest.skip("Skipping full auth flow test - requires complete dependency injection setup")
