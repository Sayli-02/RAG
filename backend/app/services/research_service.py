from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.query import SavedQuery
from app.rag.embeddings import embed_texts
from app.rag.generation import complete_with_gemini, generate_answer
from app.rag.retrieval import ScoredChunk, hybrid_search


class NeedTwoDocuments(Exception):
    """A cross-document question needs two different documents."""


class UnknownDocument(Exception):
    """The document is missing or belongs to someone else."""


class DocumentNotIndexed(Exception):
    """The document exists but has not finished indexing."""


def normalize_document_ids(document_ids: list[int]) -> list[int]:
    """Keep the first occurrence of each id. Fewer than two distinct ids is an error."""
    unique: list[int] = []
    for document_id in document_ids:
        if document_id not in unique:
            unique.append(document_id)
    if len(unique) < 2:
        raise NeedTwoDocuments
    return unique


def ask_across_documents(
    db: Session,
    user_id: int,
    question: str,
    document_ids: list[int],
) -> tuple[SavedQuery, str, list[ScoredChunk]]:
    """Search only the chosen documents, answer, and store the question."""
    chosen = normalize_document_ids(document_ids)
    for document_id in chosen:
        _owned_indexed(db, user_id, document_id)

    query_vector = embed_texts([question])[0]
    retrieved = hybrid_search(db, user_id, question, query_vector, chosen)
    answer, indexes = generate_answer(question, retrieved, complete_with_gemini)
    cited = [retrieved[index - 1] for index in indexes]

    saved = SavedQuery(user_id=user_id, query_text=question)
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return saved, answer, cited


def list_queries(db: Session, user_id: int) -> list[SavedQuery]:
    stmt = select(SavedQuery).where(SavedQuery.user_id == user_id).order_by(SavedQuery.created_at.desc())
    return list(db.scalars(stmt).all())


def _owned_indexed(db: Session, user_id: int, document_id: int) -> Document:
    document = db.scalars(
        select(Document).where(Document.id == document_id, Document.uploaded_by == user_id)
    ).first()
    if document is None:
        raise UnknownDocument
    if document.status != "indexed":
        raise DocumentNotIndexed
    return document
