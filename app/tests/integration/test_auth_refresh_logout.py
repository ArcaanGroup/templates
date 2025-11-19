"""Integration tests for refresh and logout endpoints"""


def test_refresh_token_endpoint_success(client):
    """Test successful token refresh"""
    # First, register a user to get refresh token
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "refresh_test_user",
            "email": "refresh@example.com",
            "password": "TestPass123",
        },
    )
    assert register_response.status_code == 201

    register_data = register_response.json()
    initial_refresh_token = register_data["payload"]["refresh_token"]
    initial_access_token = register_data["payload"]["access_token"]

    # Test accessing a protected route with the initial access token
    protected_response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {initial_access_token}"}
    )
    assert protected_response.status_code == 200

    # Now test refreshing the token
    refresh_response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": initial_refresh_token}
    )
    assert refresh_response.status_code == 200

    refresh_data = refresh_response.json()
    new_access_token = refresh_data["payload"]["access_token"]
    new_refresh_token = refresh_data["payload"]["refresh_token"]

    # Verify that we got new tokens
    assert new_access_token != initial_access_token
    assert new_refresh_token != initial_refresh_token

    # Test that the new access token works
    protected_response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {new_access_token}"}
    )
    assert protected_response.status_code == 200


def test_refresh_token_endpoint_invalid_token(client):
    """Test token refresh with invalid token"""
    # Try to refresh with an invalid token
    refresh_response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": "invalid_refresh_token"}
    )
    assert refresh_response.status_code == 401


def test_logout_endpoint_success(client):
    """Test successful logout"""
    # First, register a user to get tokens
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "logout_test_user",
            "email": "logout@example.com",
            "password": "TestPass123",
        },
    )
    assert register_response.status_code == 201

    register_data = register_response.json()
    refresh_token = register_data["payload"]["refresh_token"]
    access_token = register_data["payload"]["access_token"]

    # Test that access token works before logout
    protected_response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert protected_response.status_code == 200

    # Logout - send refresh token in request body
    logout_response = client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    assert logout_response.status_code == 200

    # Try to use the refresh token again - should fail
    refresh_response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_response.status_code == 401


def test_logout_endpoint_without_token(client):
    """Test logout without providing refresh token"""
    # Logout without sending refresh token
    logout_response = client.post("/api/v1/auth/logout")
    assert logout_response.status_code == 200


def test_refresh_with_revoked_token(client):
    """Test refreshing with a token that has been used and revoked"""
    # First, register a user to get tokens
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "revoked_test_user",
            "email": "revoked@example.com",
            "password": "TestPass123",
        },
    )
    assert register_response.status_code == 201

    register_data = register_response.json()
    first_refresh_token = register_data["payload"]["refresh_token"]

    # Refresh token once
    refresh_response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": first_refresh_token}
    )
    assert refresh_response.status_code == 200

    # Now try to refresh with the same token again - this should fail
    # since the old token should have been invalidated
    refresh_response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": first_refresh_token}
    )
    assert refresh_response.status_code == 401
