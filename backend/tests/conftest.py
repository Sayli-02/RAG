import os
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.core.dependencies import get_db


@pytest.fixture
def mock_db_session():
    """Fixture providing a mock database session that succeeds on queries."""
    session = MagicMock()
    session.execute.return_value = None
    return session


@pytest.fixture
def mock_failing_db_session():
    """Fixture providing a mock database session that raises an exception."""
    session = MagicMock()
    session.execute.side_effect = Exception("Database connection error")
    return session


@pytest.fixture
def client(mock_db_session):
    """TestClient with working db dependency override."""
    def _override_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def degraded_client(mock_failing_db_session):
    """TestClient with failing db dependency override."""
    def _override_get_db():
        yield mock_failing_db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
