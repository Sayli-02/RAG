from datetime import date
from pathlib import Path
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.models.document import Document, DocumentChunk, DocumentVersion

AUTHORITIES = {"RBI", "SEBI", "NPCI", "OTHER"}


def validate_pdf(filename: str | None, data: bytes) -> None:
    """Reject anything that is not a small PDF. Raises ValueError with the reason."""
    if not filename or not filename.lower().endswith(".pdf"):
        raise ValueError("File must be a PDF")
    if not data:
        raise ValueError("File is empty")
    if len(data) > settings.MAX_UPLOAD_BYTES:
        raise ValueError("PDF must be 20 MB or smaller")
    if not data.startswith(b"%PDF"):
        raise ValueError("File is not a PDF")


def save_pdf(data: bytes) -> Path:
    """Write the PDF under UPLOAD_DIR and return the path."""
    directory = Path(settings.UPLOAD_DIR)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{uuid4().hex}.pdf"
    path.write_bytes(data)
    return path


def create_document(
    db: Session,
    *,
    user_id: int,
    title: str,
    authority: str,
    category: str,
    publication_date: date | None,
    file_path: str,
) -> tuple[Document, DocumentVersion]:
    """Insert the document and its first version. Status is processing until ingestion finishes."""
    document = Document(
        title=title,
        authority=authority,
        category=category,
        publication_date=publication_date,
        uploaded_by=user_id,
        status="processing",
    )
    db.add(document)
    db.flush()
    version = DocumentVersion(
        document_id=document.id,
        version_number="1.0",
        file_path=file_path,
    )
    db.add(version)
    db.commit()
    db.refresh(document)
    db.refresh(version)
    return document, version


def list_documents(
    db: Session,
    user_id: int,
    *,
    authority: str | None = None,
    status: str | None = None,
    q: str | None = None,
) -> list[Document]:
    """Documents this user uploaded, newest first."""
    stmt = select(Document).where(Document.uploaded_by == user_id)
    if authority:
        stmt = stmt.where(Document.authority == authority)
    if status:
        stmt = stmt.where(Document.status == status)
    if q:
        stmt = stmt.where(Document.title.ilike(f"%{q}%"))
    stmt = stmt.order_by(Document.created_at.desc())
    return list(db.scalars(stmt).all())


def get_owned_document(db: Session, user_id: int, document_id: int) -> Document | None:
    """Return the document when this user owns it, including versions and chunks."""
    stmt = (
        select(Document)
        .where(Document.id == document_id, Document.uploaded_by == user_id)
        .options(selectinload(Document.versions), selectinload(Document.chunks))
    )
    return db.scalars(stmt).first()


def delete_document(db: Session, document: Document) -> None:
    """Delete chunks, the version row, the document, and the saved PDF."""
    paths = [version.file_path for version in document.versions if version.file_path]
    document_id = document.id
    db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document_id))
    db.execute(delete(DocumentVersion).where(DocumentVersion.document_id == document_id))
    db.execute(delete(Document).where(Document.id == document_id))
    db.commit()
    for path in paths:
        Path(path).unlink(missing_ok=True)
