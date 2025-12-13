"""
Basic tests for the main application
"""

import pytest


def test_root_endpoint(test_client):
    """Test the root endpoint"""
    response = test_client.get("/api")
    assert response.status_code == 200
    assert "message" in response.json()


if __name__ == "__main__":
    pytest.main()
