import pytest

from app.rag.retrieval import ScoredChunk, keep_selected
from app.services.research_service import NeedTwoDocuments, normalize_document_ids


def _chunk(chunk_id: int, document_id: int) -> ScoredChunk:
    return ScoredChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        title=f"Doc {document_id}",
        authority="RBI",
        page_number=1,
        section_heading=None,
        text="Customer data must stay confidential.",
        score=0.5,
    )


def test_keep_selected_drops_an_unselected_document():
    chunks = [_chunk(1, 1), _chunk(2, 9), _chunk(3, 2)]
    kept = keep_selected(chunks, [1, 2])
    assert [chunk.document_id for chunk in kept] == [1, 2]


def test_keep_selected_keeps_every_chunk_when_no_limit_is_set():
    chunks = [_chunk(1, 1), _chunk(2, 9)]
    assert keep_selected(chunks, None) == chunks


def test_normalize_document_ids_requires_two_distinct_documents():
    assert normalize_document_ids([4, 4, 7]) == [4, 7]
    with pytest.raises(NeedTwoDocuments):
        normalize_document_ids([4, 4])
