from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.comparison import ComparisonReport
from app.models.compliance import ComplianceChecklist, ComplianceRequirement
from app.models.document import Document, DocumentVersion
from app.models.query import SavedQuery


def analytics_summary(db: Session, user_id: int) -> dict:
    """Counts and short lists for the signed-in user's own library."""
    documents = list(
        db.scalars(select(Document).where(Document.uploaded_by == user_id).order_by(Document.updated_at.desc())).all()
    )
    by_authority: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for document in documents:
        by_authority[document.authority] = by_authority.get(document.authority, 0) + 1
        by_status[document.status] = by_status.get(document.status, 0) + 1

    topic_rows = db.execute(
        select(SavedQuery.query_text, func.count())
        .where(SavedQuery.user_id == user_id)
        .group_by(SavedQuery.query_text)
        .order_by(func.count().desc())
        .limit(5)
    ).all()
    reports = db.scalars(
        select(ComparisonReport)
        .where(ComparisonReport.user_id == user_id)
        .options(
            selectinload(ComparisonReport.version_a).selectinload(DocumentVersion.document),
            selectinload(ComparisonReport.version_b).selectinload(DocumentVersion.document),
        )
        .order_by(ComparisonReport.created_at.desc())
        .limit(5)
    ).all()
    review_rows = db.execute(
        select(ComplianceRequirement.status, func.count())
        .join(ComplianceChecklist)
        .where(ComplianceChecklist.user_id == user_id)
        .group_by(ComplianceRequirement.status)
    ).all()
    review = {status: count for status, count in review_rows}

    return {
        "documents_total": len(documents),
        "documents_indexed": by_status.get("indexed", 0),
        "by_authority": by_authority,
        "by_status": by_status,
        "recent_documents": [
            {
                "id": document.id,
                "title": document.title,
                "authority": document.authority,
                "status": document.status,
                "updated_at": document.updated_at,
            }
            for document in documents[:5]
        ],
        "frequent_queries": [{"query_text": text, "count": count} for text, count in topic_rows],
        "recent_comparisons": [
            {
                "id": report.id,
                "summary": report.summary,
                "document_a_title": report.version_a.document.title,
                "document_b_title": report.version_b.document.title,
                "created_at": report.created_at,
            }
            for report in reports
        ],
        "review": {
            "pending_review": review.get("pending_review", 0),
            "reviewed": review.get("reviewed", 0),
            "not_applicable": review.get("not_applicable", 0),
        },
    }
