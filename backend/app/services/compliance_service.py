import csv
import io

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.models.compliance import ComplianceChecklist, ComplianceRequirement
from app.models.document import Document, DocumentChunk, DocumentVersion
from app.rag.generation import complete_with_gemini
from app.rag.requirements import extract_requirements

REVIEW_STATUSES = ("pending_review", "reviewed", "not_applicable")


class UnknownDocument(Exception):
    """The document is missing or belongs to someone else."""


class DocumentNotIndexed(Exception):
    """The document exists but has not finished indexing."""


class UnknownChecklist(Exception):
    """The checklist is missing or belongs to someone else."""


class UnknownRequirement(Exception):
    """The requirement is missing or belongs to someone else."""


class BadReviewStatus(Exception):
    """The review status is not one of the three allowed values."""


def extract_checklist(db: Session, user_id: int, document_id: int) -> ComplianceChecklist:
    """Build a checklist from the latest indexed version and store it."""
    document = _owned_indexed(db, user_id, document_id)
    version = _latest_version(db, document.id)
    chunks = _chunk_payloads(db, version.id) if version is not None else []
    complete = complete_with_gemini if settings.GEMINI_API_KEY else None
    items = extract_requirements(chunks, complete)
    checklist = ComplianceChecklist(user_id=user_id, document_id=document.id, title=f"{document.title} checklist")
    db.add(checklist)
    db.flush()
    for item in items:
        db.add(
            ComplianceRequirement(
                checklist_id=checklist.id,
                requirement_text=item["requirement_text"],
                category=item["category"],
                authority=document.authority,
                source_chunk_id=item.get("chunk_id"),
                status="pending_review",
            )
        )
    db.commit()
    return get_checklist(db, user_id, checklist.id)


def list_checklists(db: Session, user_id: int) -> list[ComplianceChecklist]:
    stmt = (
        select(ComplianceChecklist)
        .where(ComplianceChecklist.user_id == user_id)
        .options(selectinload(ComplianceChecklist.document))
        .order_by(ComplianceChecklist.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def get_checklist(db: Session, user_id: int, checklist_id: int) -> ComplianceChecklist:
    stmt = (
        select(ComplianceChecklist)
        .where(ComplianceChecklist.id == checklist_id, ComplianceChecklist.user_id == user_id)
        .options(
            selectinload(ComplianceChecklist.document),
            selectinload(ComplianceChecklist.requirements).selectinload(ComplianceRequirement.source_chunk),
        )
    )
    checklist = db.scalars(stmt).first()
    if checklist is None:
        raise UnknownChecklist
    return checklist


def update_requirement(
    db: Session,
    user_id: int,
    requirement_id: int,
    status: str,
    reviewer_notes: str | None,
) -> ComplianceRequirement:
    if status not in REVIEW_STATUSES:
        raise BadReviewStatus
    requirement = db.scalars(
        select(ComplianceRequirement)
        .join(ComplianceChecklist)
        .where(ComplianceRequirement.id == requirement_id, ComplianceChecklist.user_id == user_id)
        .options(selectinload(ComplianceRequirement.source_chunk))
    ).first()
    if requirement is None:
        raise UnknownRequirement
    requirement.status = status
    requirement.reviewer_notes = reviewer_notes
    db.commit()
    db.refresh(requirement)
    return requirement


def checklist_csv(checklist: ComplianceChecklist) -> str:
    """One row per requirement. Page comes from the source chunk when it is still stored."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["requirement", "category", "authority", "page", "status", "notes"])
    for requirement in checklist.requirements:
        page = requirement.source_chunk.page_number if requirement.source_chunk is not None else ""
        writer.writerow(
            [
                requirement.requirement_text,
                requirement.category or "",
                requirement.authority or "",
                page,
                requirement.status,
                requirement.reviewer_notes or "",
            ]
        )
    return buffer.getvalue()


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
    return [{"chunk_id": chunk.id, "text": chunk.chunk_text, "page": chunk.page_number} for chunk in chunks]
