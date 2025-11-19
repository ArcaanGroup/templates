"""End-to-end tests for authentication flow"""

import pytest
import uuid
from fastapi.testclient import TestClient


class TestAuthFlow:
    """End-to-end tests for the complete authentication flow"""

    def test_auth_flow_complete(self, client):
        """Test the complete authentication flow: register -> login -> change password"""
        # Use a unique username for each test run
        unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
        unique_email = f"{unique_username}@example.com"

        # 1. Register a new user
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "username": unique_username,
                "email": unique_email,
                "password": "TestPass123",
            },
        )

        print(f"Register response status: {register_response.status_code}")
        print(f"Register response: {register_response.json()}")

        # Check that registration was successful
        assert register_response.status_code == 201
        register_data = register_response.json()
        assert register_data["success"] is True

        # 2. Login with the registered user
        login_response = client.post(
            "/api/v1/auth/login", data={"username": unique_username, "password": "TestPass123"}
        )

        print(f"Login response status: {login_response.status_code}")
        print(f"Login response: {login_response.json()}")

        # Check that login was successful
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert login_data["success"] is True

        # Extract tokens
        token_data = login_data["payload"]
        access_token = token_data["access_token"]
        refresh_token = token_data.get("refresh_token")

        # 3. Test change password
        change_password_response = client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "TestPass123", "new_password": "NewTestPass456"},
            headers={"Authorization": f"Bearer {access_token}"},
        )

        print(f"Change password response status: {change_password_response.status_code}")
        print(f"Change password response: {change_password_response.json()}")

        # Check that password change was successful
        assert change_password_response.status_code == 200
        change_password_data = change_password_response.json()
        assert change_password_data["success"] is True
