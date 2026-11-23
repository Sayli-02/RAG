import app.models  # noqa: F401
import pytest
from fastapi.testclient import TestClient
from pgvector.sqlalchemy import Vector
from sqlalchemy import create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.dependencies import get_db
from app.main import app
from app.models.chat import Citation, Conversation, Message
from app.models.document import Document, DocumentChunk, DocumentVersion
from app.models.user import User
from app.rag.generation import NOT_ENOUGH
from app.rag.retrieval import ScoredChunk


@compiles(Vector, "sqlite")
def _compile_vector_for_sqlite(element, compiler, **kw):
    return "TEXT"


@pytest.fixture
def assistant_client(monkeypatch):
    """SQLite chat tables. Search and Gemini are fakes unless a test replaces them."""
    monkeypatch.setattr(
        "app.services.assistant_service.embed_texts",
        lambda texts: [[0.0] * 384],
    )
    monkeypatch.setattr("app.services.assistant_service.hybrid_search", lambda *args, **kwargs: [])
    def _gemini_must_not_run(prompt: str) -> str:
        raise AssertionError("Gemini should not be called")

    monkeypatch.setattr("app.services.assistant_service.complete_with_gemini", _gemini_must_not_run)

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    for table in (
        User.__table__,
        Document.__table__,
        DocumentVersion.__table__,
        DocumentChunk.__table__,
        Conversation.__table__,
        Message.__table__,
        Citation.__table__,
    ):
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
        yield client, Session
    app.dependency_overrides.clear()
    engine.dispose()


def _auth(client: TestClient, email: str) -> dict[str, str]:
    assert client.post(
        "/auth/register",
        json={"name": "Officer", "email": email, "password": "correct-horse"},
    ).status_code == 201
    login = client.post("/auth/login", data={"username": email, "password": "correct-horse"})
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_ask_without_chunks_skips_gemini(assistant_client):
    client, _session = assistant_client
    headers = _auth(client, "owner@example.com")
    response = client.post("/assistant/ask", headers=headers, json={"question": "What is the APR?"})
    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == NOT_ENOUGH
    assert body["citations"] == []


def test_ask_saves_a_page_citation(assistant_client, monkeypatch):
    client, Session = assistant_client
    headers = _auth(client, "owner@example.com")
    user_id = client.get("/auth/me", headers=headers).json()["id"]

    db = Session()
    document = Document(
        title="Digital Lending",
        authority="RBI",
        category="Circular",
        status="indexed",
        uploaded_by=user_id,
    )
    db.add(document)
    db.flush()
    chunk = DocumentChunk(
        document_id=document.id,
        chunk_text="Lenders must disclose the annual percentage rate.",
        page_number=3,
        metadata_={"section_heading": "Disclosures"},
    )
    db.add(chunk)
    db.commit()
    found = ScoredChunk(
        chunk_id=chunk.id,
        document_id=document.id,
        title=document.title,
        authority=document.authority,
        page_number=3,
        section_heading="Disclosures",
        text=chunk.chunk_text,
        score=0.8,
    )
    db.close()

    monkeypatch.setattr("app.services.assistant_service.hybrid_search", lambda *args, **kwargs: [found])
    monkeypatch.setattr(
        "app.services.assistant_service.complete_with_gemini",
        lambda prompt: "Lenders must disclose the annual percentage rate [1].",
    )

    response = client.post("/assistant/ask", headers=headers, json={"question": "What must lenders disclose?"})
    assert response.status_code == 200
    body = response.json()
    assert body["citations"][0]["page_number"] == 3
    assert body["citations"][0]["section"] == "Disclosures"
    assert body["citations"][0]["document_title"] == "Digital Lending"
    assert "[1]" in body["answer"]

    detail = client.get(f"/assistant/conversations/{body['conversation_id']}", headers=headers)
    assert detail.status_code == 200
    messages = detail.json()["messages"]
    assert [message["role"] for message in messages] == ["user", "assistant"]
    assert messages[1]["citations"][0]["page_number"] == 3

    other = _auth(client, "other@example.com")
    assert client.get(f"/assistant/conversations/{body['conversation_id']}", headers=other).status_code == 404
    assert client.get("/assistant/conversations", headers=other).json() == []
