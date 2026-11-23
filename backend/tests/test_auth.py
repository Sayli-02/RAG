import app.models  # noqa: F401  — register related models before querying User
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.dependencies import get_db
from app.main import app
from app.models.user import User


@pytest.fixture
def auth_client():
    """HTTP client backed by a fresh SQLite users table. No Postgres required."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    User.__table__.create(engine)
    Session = sessionmaker(bind=engine)

    def override_get_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
    engine.dispose()


def _register(client: TestClient, email: str = "ada@example.com", password: str = "correct-horse"):
    return client.post(
        "/auth/register",
        json={"name": "Ada Lovelace", "email": email, "password": password},
    )


def test_register_returns_public_user(auth_client):
    response = _register(auth_client)
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "ada@example.com"
    assert body["name"] == "Ada Lovelace"
    assert body["role"] == "user"
    assert "password" not in body
    assert "password_hash" not in body


def test_register_rejects_duplicate_email(auth_client):
    assert _register(auth_client).status_code == 201
    again = _register(auth_client, email="Ada@Example.com")
    assert again.status_code == 409


def test_register_rejects_short_password(auth_client):
    response = _register(auth_client, password="short")
    assert response.status_code == 422


def test_login_returns_token_and_me_returns_that_user(auth_client):
    assert _register(auth_client).status_code == 201
    login = auth_client.post(
        "/auth/login",
        data={"username": "ADA@example.com", "password": "correct-horse"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    assert login.json()["token_type"] == "bearer"

    me = auth_client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "ada@example.com"


def test_login_rejects_wrong_password(auth_client):
    assert _register(auth_client).status_code == 201
    response = auth_client.post(
        "/auth/login",
        data={"username": "ada@example.com", "password": "wrong-horse"},
    )
    assert response.status_code == 401


def test_me_rejects_missing_token(auth_client):
    response = auth_client.get("/auth/me")
    assert response.status_code == 401
