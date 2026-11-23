import re
from dataclasses import dataclass

from rank_bm25 import BM25Okapi
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document import Document, DocumentChunk

# Standard reciprocal-rank-fusion constant. Rank 1 contributes 1/61.
RRF_K = 60


@dataclass
class ScoredChunk:
    """One retrieved passage, plus the document fields a citation needs."""

    chunk_id: int
    document_id: int
    title: str
    authority: str
    page_number: int | None
    section_heading: str | None
    text: str
    score: float


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def bm25_rank(texts: list[str], query: str, k: int) -> list[tuple[int, float]]:
    """Return (index, score) for texts that share words with the query, best first."""
    query_tokens = tokenize(query)
    tokenized = [tokenize(text) for text in texts]
    if not query_tokens or not any(tokenized):
        return []
    # BM25Okapi cannot score an empty document list. Empty rows are kept as [] so indexes stay aligned.
    safe = [tokens if tokens else ["__empty__"] for tokens in tokenized]
    scores = BM25Okapi(safe).get_scores(query_tokens)
    ranked = [(index, float(score)) for index, score in enumerate(scores) if score > 0 and tokenized[index]]
    ranked.sort(key=lambda item: item[1], reverse=True)
    return ranked[:k]


def reciprocal_rank_fusion(rankings: list[list[int]]) -> list[tuple[int, float]]:
    """Merge ranked id lists. An id near the top of either list scores higher."""
    scores: dict[int, float] = {}
    for ranking in rankings:
        for rank, item_id in enumerate(ranking):
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (RRF_K + rank + 1)
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


def _heading(chunk: DocumentChunk) -> str | None:
    metadata = chunk.metadata_ or {}
    heading = metadata.get("section_heading")
    return heading or None


def keep_selected(chunks: list[ScoredChunk], document_ids: list[int] | None) -> list[ScoredChunk]:
    """Drop chunks from documents the caller did not pick. None keeps every chunk."""
    if document_ids is None:
        return chunks
    allowed = set(document_ids)
    return [chunk for chunk in chunks if chunk.document_id in allowed]


def _owned_rows(db: Session, user_id: int, document_ids: list[int] | None = None):
    stmt = (
        select(DocumentChunk, Document)
        .join(Document, Document.id == DocumentChunk.document_id)
        .where(Document.uploaded_by == user_id, Document.status == "indexed")
    )
    if document_ids is not None:
        stmt = stmt.where(Document.id.in_(document_ids))
    return db.execute(stmt).all()


def vector_search(
    db: Session,
    user_id: int,
    query_vector: list[float],
    k: int,
    document_ids: list[int] | None = None,
) -> list[ScoredChunk]:
    """Nearest chunks by pgvector cosine distance. Lower distance is a closer meaning."""
    distance = DocumentChunk.embedding.cosine_distance(query_vector)
    stmt = (
        select(DocumentChunk, Document, distance.label("distance"))
        .join(Document, Document.id == DocumentChunk.document_id)
        .where(
            Document.uploaded_by == user_id,
            Document.status == "indexed",
            DocumentChunk.embedding.is_not(None),
        )
        .order_by(distance)
        .limit(k)
    )
    if document_ids is not None:
        stmt = stmt.where(Document.id.in_(document_ids))
    rows = db.execute(stmt).all()
    return [
        ScoredChunk(
            chunk_id=chunk.id,
            document_id=document.id,
            title=document.title,
            authority=document.authority,
            page_number=chunk.page_number,
            section_heading=_heading(chunk),
            text=chunk.chunk_text,
            score=1.0 - float(dist),
        )
        for chunk, document, dist in rows
    ]


def bm25_search(
    db: Session,
    user_id: int,
    query: str,
    k: int,
    document_ids: list[int] | None = None,
) -> list[ScoredChunk]:
    """Keyword rank over this user's indexed chunks.

    shortcut: loads every indexed chunk for the user into memory. Move this to
    Postgres full-text search when one user has more documents than fit comfortably in RAM.
    """
    rows = _owned_rows(db, user_id, document_ids)
    ranked = bm25_rank([chunk.chunk_text for chunk, _document in rows], query, k)
    found: list[ScoredChunk] = []
    for index, score in ranked:
        chunk, document = rows[index]
        found.append(
            ScoredChunk(
                chunk_id=chunk.id,
                document_id=document.id,
                title=document.title,
                authority=document.authority,
                page_number=chunk.page_number,
                section_heading=_heading(chunk),
                text=chunk.chunk_text,
                score=score,
            )
        )
    return found


def fuse(semantic: list[ScoredChunk], keyword: list[ScoredChunk]) -> list[ScoredChunk]:
    """Order chunks by reciprocal rank fusion. The score on each result is the fused rank score."""
    by_id: dict[int, ScoredChunk] = {}
    for chunk in semantic + keyword:
        by_id.setdefault(chunk.chunk_id, chunk)
    fused = reciprocal_rank_fusion(
        [[chunk.chunk_id for chunk in semantic], [chunk.chunk_id for chunk in keyword]]
    )
    return [
        ScoredChunk(
            chunk_id=chunk_id,
            document_id=by_id[chunk_id].document_id,
            title=by_id[chunk_id].title,
            authority=by_id[chunk_id].authority,
            page_number=by_id[chunk_id].page_number,
            section_heading=by_id[chunk_id].section_heading,
            text=by_id[chunk_id].text,
            score=score,
        )
        for chunk_id, score in fused
    ]


def hybrid_search(
    db: Session,
    user_id: int,
    question: str,
    query_vector: list[float],
    document_ids: list[int] | None = None,
) -> list[ScoredChunk]:
    """Semantic top-k, keyword top-k, fuse, then rerank down to RERANK_K.

    document_ids limits the search to those documents. The assistant passes None
    and still searches everything the user has indexed.
    """
    from app.rag.reranking import rerank

    semantic = vector_search(db, user_id, query_vector, settings.RETRIEVAL_K, document_ids)
    keyword = bm25_search(db, user_id, question, settings.RETRIEVAL_K, document_ids)
    return rerank(question, keep_selected(fuse(semantic, keyword), document_ids))
