import app.models  # noqa: F401
import fitz
import pytest
from fastapi.testclient import TestClient
from pgvector.sqlalchemy import Vector
from sqlalchemy import create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.dependencies import get_db
from app.main import app
from app.models.document import Document, DocumentChunk, DocumentVersion
from app.models.user import User
from app.services.document_service import validate_pdf


@compiles(Vector, "sqlite")
def _compile_vector_for_sqlite(element, compiler, **kw):
    return "TEXT"


@pytest.fixture
def docs_client(tmp_path, monkeypatch):
    """Auth plus documents tables on SQLite. Ingestion is patched so Postgres is not required."""
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path))
    monkeypatch.setattr("app.api.documents.ingest_document", lambda *args, **kwargs: None)

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    for table in (User.__table__, Document.__table__, DocumentVersion.__table__, DocumentChunk.__table__):
        table.create(engine)
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


def _pdf_bytes() -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "Digital lending instructions")
    data = document.tobytes()
    document.close()
    return data


def _auth_header(client: TestClient, email: str) -> dict[str, str]:
    registered = client.post(
        "/auth/register",
        json={"name": "Officer", "email": email, "password": "correct-horse"},
    )
    assert registered.status_code == 201
    login = client.post("/auth/login", data={"username": email, "password": "correct-horse"})
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def _upload(client: TestClient, headers: dict[str, str], title: str = "Digital Lending"):
    return client.post(
        "/documents/upload",
        headers=headers,
        data={"title": title, "authority": "RBI", "category": "Circular"},
        files={"file": ("circular.pdf", _pdf_bytes(), "application/pdf")},
    )


def test_validate_pdf_rejects_wrong_type_and_oversize():
    with pytest.raises(ValueError):
        validate_pdf("notes.txt", b"%PDF-1.4")
    with pytest.raises(ValueError):
        validate_pdf("notes.pdf", b"not a pdf")
    with pytest.raises(ValueError):
        validate_pdf("notes.pdf", b"%PDF" + b"x" * settings.MAX_UPLOAD_BYTES)


def test_upload_requires_token(docs_client):
    response = _upload(docs_client, {})
    assert response.status_code == 401


def test_upload_list_and_owner_isolation(docs_client):
    owner = _auth_header(docs_client, "owner@example.com")
    other = _auth_header(docs_client, "other@example.com")

    created = _upload(docs_client, owner)
    assert created.status_code == 201
    body = created.json()
    assert body["status"] == "processing"
    assert body["authority"] == "RBI"
    assert "password" not in body

    listing = docs_client.get("/documents", headers=owner)
    assert listing.status_code == 200
    assert len(listing.json()) == 1
    assert docs_client.get("/documents", headers=other).json() == []

    document_id = body["id"]
    detail = docs_client.get(f"/documents/{document_id}", headers=owner)
    assert detail.status_code == 200
    assert detail.json()["versions"][0]["version_number"] == "1.0"
    assert detail.json()["chunks"] == []
    assert docs_client.get(f"/documents/{document_id}", headers=other).status_code == 404


def test_upload_rejects_non_pdf(docs_client):
    headers = _auth_header(docs_client, "owner@example.com")
    response = docs_client.post(
        "/documents/upload",
        headers=headers,
        data={"title": "Nope", "authority": "RBI", "category": "Circular"},
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400


def test_delete_removes_document_and_file(docs_client, tmp_path):
    headers = _auth_header(docs_client, "owner@example.com")
    created = _upload(docs_client, headers)
    document_id = created.json()["id"]
    assert list(tmp_path.glob("*.pdf"))

    deleted = docs_client.delete(f"/documents/{document_id}", headers=headers)
    assert deleted.status_code == 204
    assert docs_client.get(f"/documents/{document_id}", headers=headers).status_code == 404
    assert list(tmp_path.glob("*.pdf")) == []
