from app.models import (
    User,
    Document,
    DocumentVersion,
    DocumentChunk,
    Conversation,
    Message,
    Citation,
    ComparisonReport,
    ComplianceChecklist,
    ComplianceRequirement,
    SavedQuery,
    EvaluationRun,
)


def test_model_table_names():
    """Verify that all ORM models define the expected database table names."""
    assert User.__tablename__ == "users"
    assert Document.__tablename__ == "documents"
    assert DocumentVersion.__tablename__ == "document_versions"
    assert DocumentChunk.__tablename__ == "document_chunks"
    assert Conversation.__tablename__ == "conversations"
    assert Message.__tablename__ == "messages"
    assert Citation.__tablename__ == "citations"
    assert ComparisonReport.__tablename__ == "comparison_reports"
    assert ComplianceChecklist.__tablename__ == "compliance_checklists"
    assert ComplianceRequirement.__tablename__ == "compliance_requirements"
    assert SavedQuery.__tablename__ == "saved_queries"
    assert EvaluationRun.__tablename__ == "evaluation_runs"


def test_user_instantiation():
    """Verify User model attributes and defaults."""
    user = User(
        name="Test Compliance Officer",
        email="compliance@example.com",
        password_hash="hashed_secret",
        role="user",
    )
    assert user.name == "Test Compliance Officer"
    assert user.email == "compliance@example.com"
    assert user.role == "user"


def test_document_and_chunk_instantiation():
    """Verify Document and DocumentChunk model attributes."""
    doc = Document(
        title="RBI Master Direction - Digital Lending",
        authority="RBI",
        category="Master Direction",
        status="uploaded",
        uploaded_by=1,
    )
    assert doc.title == "RBI Master Direction - Digital Lending"
    assert doc.authority == "RBI"

    chunk = DocumentChunk(
        document_id=1,
        chunk_text="Digital Lending Guidelines section 3...",
        page_number=5,
        metadata_={"heading": "Section 3: Disclosures"},
    )
    assert chunk.document_id == 1
    assert chunk.page_number == 5
    assert chunk.metadata_["heading"] == "Section 3: Disclosures"

