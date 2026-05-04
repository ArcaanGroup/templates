"""
Pytest configuration file
"""

import sys
from pathlib import Path

import pytest

# Add the app directory to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))


@pytest.fixture(scope="session")
def test_client():
    """
    Create a test client for API requests
    """
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app)


@pytest.fixture(scope="function")
def db_session():
    """
    Create a database session for tests
    """
    from unittest.mock import MagicMock

    from app.infra.core.database import get_db_session
    from app.main import app

    session = MagicMock()
    app.dependency_overrides[get_db_session] = lambda: session
    yield session
    app.dependency_overrides.clear()
