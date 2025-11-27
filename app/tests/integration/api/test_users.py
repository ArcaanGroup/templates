"""Integration tests for User API endpoints"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the API"""
    with TestClient(app) as test_client:
        yield test_client


class TestUserEndpoints:
    """Test cases for User API endpoints"""

    def test_create_user(self, client: TestClient):
        """Test creating a new user"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]  # Short unique identifier
        payload = {
            "username": f"testuser{unique_id}",
            "email": f"testuser{unique_id}@example.com",
            "password": "SecurePass123",
            "is_active": True
        }

        response = client.post("/api/v1/users/", json=payload)
        assert response.status_code == 201

        data = response.json()
        assert data["success"] is True
        assert data["payload"]["username"] == f"testuser{unique_id}"
        assert data["payload"]["email"] == f"testuser{unique_id}@example.com"
        assert data["payload"]["is_active"] is True
        assert "id" in data["payload"]
        assert "created_at" in data["payload"]
        assert "updated_at" in data["payload"]

    def test_create_user_conflict(self, client: TestClient):
        """Test creating a user that already exists"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]  # Short unique identifier
        # First, create a user
        payload = {
            "username": f"conflictuser{unique_id}",
            "email": f"conflict{unique_id}@example.com",
            "password": "SecurePass123",
            "is_active": True
        }
        response = client.post("/api/v1/users/", json=payload)
        assert response.status_code == 201

        # Try to create the same user again
        response = client.post("/api/v1/users/", json=payload)
        assert response.status_code == 409

    def test_get_user(self, client: TestClient):
        """Test getting a user by ID"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]  # Short unique identifier
        # First, create a user (public endpoint)
        payload = {
            "username": f"getusertest{unique_id}",
            "email": f"getuser{unique_id}@example.com",
            "password": "SecurePass123",
            "is_active": True
        }
        create_response = client.post("/api/v1/users/", json=payload)
        assert create_response.status_code == 201
        created_user_id = create_response.json()["payload"]["id"]

        # Login to get a token
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": f"getusertest{unique_id}", "password": "SecurePass123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["payload"]["access_token"]

        # Make authenticated request to get the user
        response = client.get(
            f"/api/v1/users/{created_user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["payload"]["id"] == created_user_id
        assert data["payload"]["username"] == f"getusertest{unique_id}"
        assert data["payload"]["email"] == f"getuser{unique_id}@example.com"

    def test_get_user_not_found(self, client: TestClient):
        """Test getting a non-existent user"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        # Create a user to login with
        register_payload = {
            "username": f"testuser{unique_id}",
            "email": f"test{unique_id}@example.com",
            "password": "SecurePass123",
            "is_active": True
        }
        register_response = client.post("/api/v1/users/", json=register_payload)
        assert register_response.status_code == 201

        # Login with the created user
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": f"testuser{unique_id}", "password": "SecurePass123"}
        )

        assert login_response.status_code == 200
        token = login_response.json()["payload"]["access_token"]

        # Make authenticated request to get a non-existent user
        response = client.get(
            "/api/v1/users/999999",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404

    def test_update_user(self, client: TestClient):
        """Test updating a user"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]  # Short unique identifier
        # First, create a user
        create_payload = {
            "username": f"updateuser{unique_id}",
            "email": f"update{unique_id}@example.com",
            "password": "SecurePass123",
            "is_active": True
        }
        create_response = client.post("/api/v1/users/", json=create_payload)
        assert create_response.status_code == 201
        user_id = create_response.json()["payload"]["id"]

        # Login to get a token
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": f"updateuser{unique_id}", "password": "SecurePass123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["payload"]["access_token"]

        # Update the user with authentication
        update_payload = {
            "username": f"updateduser{unique_id}",
            "email": f"updated{unique_id}@example.com",
            "is_active": False
        }
        response = client.put(
            f"/api/v1/users/{user_id}",
            json=update_payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["payload"]["username"] == f"updateduser{unique_id}"
        assert data["payload"]["email"] == f"updated{unique_id}@example.com"
        assert data["payload"]["is_active"] is False

    def test_update_user_not_found(self, client: TestClient):
        """Test updating a non-existent user"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        # Create a user to login with
        payload = {
            "username": f"testuser{unique_id}",
            "email": f"test{unique_id}@example.com",
            "password": "SecurePass123",
            "is_active": True
        }
        create_response = client.post("/api/v1/users/", json=payload)
        assert create_response.status_code == 201

        # Login to get a token
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": f"testuser{unique_id}", "password": "SecurePass123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["payload"]["access_token"]

        # Try to update a non-existent user with authentication
        update_payload = {
            "username": "updateduser",
        }
        response = client.put(
            "/api/v1/users/999999",
            json=update_payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404

    def test_delete_user(self, client: TestClient):
        """Test deleting a user"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]  # Short unique identifier
        # First, create a user
        payload = {
            "username": f"deleteuser{unique_id}",
            "email": f"delete{unique_id}@example.com",
            "password": "SecurePass123",
            "is_active": True
        }
        create_response = client.post("/api/v1/users/", json=payload)
        assert create_response.status_code == 201
        user_id = create_response.json()["payload"]["id"]

        # Login to get a token
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": f"deleteuser{unique_id}", "password": "SecurePass123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["payload"]["access_token"]

        # Delete the user with authentication
        response = client.delete(
            f"/api/v1/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 204

        # Verify the user is gone
        # Login again to get a token for this request
        get_login_response = client.post(
            "/api/v1/auth/login",
            data={"username": f"deleteuser{unique_id}", "password": "SecurePass123"}
        )
        assert get_login_response.status_code == 404

    def test_delete_user_not_found(self, client: TestClient):
        """Test deleting a non-existent user"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        # Create a user to login with
        payload = {
            "username": f"testuser{unique_id}",
            "email": f"test{unique_id}@example.com",
            "password": "SecurePass123",
            "is_active": True
        }
        create_response = client.post("/api/v1/users/", json=payload)
        assert create_response.status_code == 201

        # Login to get a token
        login_response = client.post(
            "/api/v1/auth/login",
            data={"username": f"testuser{unique_id}", "password": "SecurePass123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["payload"]["access_token"]

        # Try to delete a non-existent user with authentication
        response = client.delete(
            "/api/v1/users/999999",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404

    def test_list_users(self, client: TestClient):
        """Test listing users"""
        import uuid
        # Create a few users first with unique identifiers
        created_user_ids = []
        for i in range(3):
            unique_id = str(uuid.uuid4())[:8]  # Short unique identifier
            payload = {
                "username": f"listuser{unique_id}{i}",
                "email": f"listuser{unique_id}{i}@example.com",
                "password": "SecurePass123",
                "is_active": True
            }
            response = client.post("/api/v1/users/", json=payload)
            assert response.status_code == 201
            created_user_ids.append(response.json()["payload"]["id"])

        # List the users
        response = client.get("/api/v1/users/")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert len(data["payload"]["items"]) >= 3  # May include users from other tests
        assert data["payload"]["total"] >= 3
