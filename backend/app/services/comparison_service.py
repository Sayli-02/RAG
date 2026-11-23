from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.models.comparison import ComparisonReport
from app.models.document import Document, DocumentChunk, DocumentVersion
from app.rag.diffing import build_diff, summarize_diff
from app.rag.generation import complete_with_gemini


class UnknownDocument(Exception):
    """The document is missing or belongs to someone else."""


class DocumentNotIndexed(Exception):
    """The document exists but has not finished indexing."""


class SameDocument(Exception):
    """Both sides of a comparison are the same document."""


class UnknownReport(Exception):
    """The report is missing or belongs to someone else."""


def compare_documents(db: Session, user_id: int, document_a_id: int, document_b_id: int) -> ComparisonReport:
    """Diff the latest versions of two owned documents and store the report."""
    if document_a_id == document_b_id:
        raise SameDocument
    older_doc = _owned_indexed(db, user_id, document_a_id)
    newer_doc = _owned_indexed(db, user_id, document_b_id)
    older_version = _latest_version(db, older_doc.id)
    newer_version = _latest_version(db, newer_doc.id)
    if older_version is None or newer_version is None:
        raise UnknownDocument

    diff = build_diff(_chunk_payloads(db, older_version.id), _chunk_payloads(db, newer_version.id))
    complete = complete_with_gemini if settings.GEMINI_API_KEY else None
    summary, affected = summarize_diff(diff, complete)
    diff["affected_requirements"] = affected
    report = ComparisonReport(
        user_id=user_id,
        version_a_id=older_version.id,
        version_b_id=newer_version.id,
        report_json=diff,
        summary=summary,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def list_reports(db: Session, user_id: int) -> list[ComparisonReport]:
    stmt = (
        select(ComparisonReport)
        .where(ComparisonReport.user_id == user_id)
        .options(
            selectinload(ComparisonReport.version_a).selectinload(DocumentVersion.document),
            selectinload(ComparisonReport.version_b).selectinload(DocumentVersion.document),
        )
        .order_by(ComparisonReport.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def get_report(db: Session, user_id: int, report_id: int) -> ComparisonReport:
    stmt = (
        select(ComparisonReport)
        .where(ComparisonReport.id == report_id, ComparisonReport.user_id == user_id)
        .options(
            selectinload(ComparisonReport.version_a).selectinload(DocumentVersion.document),
            selectinload(ComparisonReport.version_b).selectinload(DocumentVersion.document),
        )
    )
    report = db.scalars(stmt).first()
    if report is None:
        raise UnknownReport
    return report


def _owned_indexed(db: Session, user_id: int, document_id: int) -> Document:
    document = db.scalars(
        select(Document).where(Document.id == document_id, Document.uploaded_by == user_id)
    ).first()
    if document is None:
        raise UnknownDocument
    if document.status != "indexed":
        raise DocumentNotIndexed
    return document


def _latest_version(db: Session, document_id: int) -> DocumentVersion | None:
    return db.scalars(
        select(DocumentVersion)
        .where(DocumentVersion.document_id == document_id)
        .order_by(DocumentVersion.id.desc())
    ).first()


def _chunk_payloads(db: Session, version_id: int) -> list[dict]:
    chunks = db.scalars(
        select(DocumentChunk).where(DocumentChunk.version_id == version_id).order_by(DocumentChunk.id)
    ).all()
    payloads = []
    for chunk in chunks:
        embedding = None
        if chunk.embedding is not None:
            embedding = [float(value) for value in chunk.embedding]
        payloads.append(
            {
                "chunk_id": chunk.id,
                "page": chunk.page_number,
                "text": chunk.chunk_text,
                "embedding": embedding,
            }
        )
    return payloads


