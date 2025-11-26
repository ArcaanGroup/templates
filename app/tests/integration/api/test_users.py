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
        # First, create a user
        payload = {
            "username": f"getusertest{unique_id}",
            "email": f"getuser{unique_id}@example.com",
            "password": "SecurePass123",
            "is_active": True
        }
        create_response = client.post("/api/v1/users/", json=payload)
        assert create_response.status_code == 201
        user_id = create_response.json()["payload"]["id"]

        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["payload"]["id"] == user_id
        assert data["payload"]["username"] == f"getusertest{unique_id}"
        assert data["payload"]["email"] == f"getuser{unique_id}@example.com"

    def test_get_user_not_found(self, client: TestClient):
        """Test getting a non-existent user"""
        response = client.get("/api/v1/users/999999")
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

        # Update the user
        update_payload = {
            "username": f"updateduser{unique_id}",
            "email": f"updated{unique_id}@example.com",
            "is_active": False
        }
        response = client.put(f"/api/v1/users/{user_id}", json=update_payload)
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["payload"]["username"] == f"updateduser{unique_id}"
        assert data["payload"]["email"] == f"updated{unique_id}@example.com"
        assert data["payload"]["is_active"] is False

    def test_update_user_not_found(self, client: TestClient):
        """Test updating a non-existent user"""
        update_payload = {
            "username": "updateduser",
        }
        response = client.put("/api/v1/users/999999", json=update_payload)
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

        # Delete the user
        response = client.delete(f"/api/v1/users/{user_id}")
        assert response.status_code == 204

        # Verify the user is gone
        get_response = client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == 404

    def test_delete_user_not_found(self, client: TestClient):
        """Test deleting a non-existent user"""
        response = client.delete("/api/v1/users/999999")
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


class TestUserRolesEndpoints:
    """Test cases for User Role API endpoints"""

    def test_assign_roles_to_user(self, client: TestClient):
        """Test assigning roles to a user"""
        import uuid
        unique_id = str(uuid.uuid4())[:5]  # Shorter unique identifier to ensure username length <= 20

        # First, create a user
        user_payload = {
            "username": f"tusr{unique_id}",
            "email": f"testuser_roles{unique_id}@example.com",
            "password": "SecurePass123",
            "is_active": True,
            "role_ids": []  # Add the required field for the updated DTO
        }
        create_user_response = client.post("/api/v1/users/", json=user_payload)
        assert create_user_response.status_code == 201
        user_id = create_user_response.json()["payload"]["id"]

        # Create a role first
        role_payload = {
            "title": f"test_role_{unique_id}",
            "description": f"Test role for user {unique_id}",
            "permissions": []
        }
        create_role_response = client.post("/api/v1/roles/", json=role_payload)
        assert create_role_response.status_code == 200
        role_id = create_role_response.json()["payload"]["id"]

        # Assign the role to the user
        role_assignment_payload = {
            "user_id": user_id,
            "role_ids": [role_id]
        }
        assign_response = client.post(f"/api/v1/users/{user_id}/roles", json=role_assignment_payload)
        assert assign_response.status_code == 201

        data = assign_response.json()
        assert data["success"] is True
        assert data["payload"]["id"] == user_id
        assert len(data["payload"]["roles"]) >= 1  # May include default roles

    def test_get_user_roles(self, client: TestClient):
        """Test getting roles for a user"""
        import uuid
        unique_id = str(uuid.uuid4())[:5]  # Shorter unique identifier to ensure username length <= 20

        # First, create a user
        user_payload = {
            "username": f"tusr2{unique_id}",
            "email": f"testuser_getroles{unique_id}@example.com",
            "password": "SecurePass123",
            "is_active": True,
            "role_ids": []  # Add the required field for the updated DTO
        }
        create_user_response = client.post("/api/v1/users/", json=user_payload)
        assert create_user_response.status_code == 201
        user_id = create_user_response.json()["payload"]["id"]

        # Create a role first
        role_payload = {
            "title": f"test_role_get_{unique_id}",
            "description": f"Test role for user {unique_id}",
            "permissions": []
        }
        create_role_response = client.post("/api/v1/roles/", json=role_payload)
        assert create_role_response.status_code == 200
        role_id = create_role_response.json()["payload"]["id"]

        # Assign the role to the user
        role_assignment_payload = {
            "user_id": user_id,
            "role_ids": [role_id]
        }
        assign_response = client.post(f"/api/v1/users/{user_id}/roles", json=role_assignment_payload)
        assert assign_response.status_code == 201

        # Get the user's roles
        get_roles_response = client.get(f"/api/v1/users/{user_id}/roles")
        assert get_roles_response.status_code == 200

        data = get_roles_response.json()
        assert data["success"] is True
        assert data["payload"]["id"] == user_id
        assert data["payload"]["username"] == f"tusr2{unique_id}"
        assert f"test_role_get_{unique_id}" in data["payload"]["roles"]  # Check that our role appears in the response

    def test_get_user_roles_not_found(self, client: TestClient):
        """Test getting roles for a non-existent user"""
        response = client.get("/api/v1/users/999999/roles")
        assert response.status_code == 404
