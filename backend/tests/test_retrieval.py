import pytest

from app.core.config import settings
from app.rag.generation import NOT_ENOUGH, cited_indexes, generate_answer
from app.rag.reranking import rerank
from app.rag.retrieval import ScoredChunk, bm25_rank, reciprocal_rank_fusion


def _chunk(chunk_id: int, text: str) -> ScoredChunk:
    return ScoredChunk(
        chunk_id=chunk_id,
        document_id=1,
        title="Digital Lending",
        authority="RBI",
        page_number=chunk_id,
        section_heading=None,
        text=text,
        score=0.0,
    )


def test_bm25_ranks_the_rare_word_first():
    texts = [
        "The weather is mild today",
        "NBFC lenders must disclose the annual percentage rate",
        "Payment systems settle overnight",
    ]
    ranked = bm25_rank(texts, "NBFC disclose", k=3)
    assert ranked[0][0] == 1
    assert ranked[0][1] > 0


def test_bm25_ignores_a_query_with_no_shared_words():
    assert bm25_rank(["lenders must disclose"], "volcano", k=3) == []


def test_reciprocal_rank_fusion_prefers_a_chunk_in_both_lists():
    fused = reciprocal_rank_fusion([[1, 2, 3], [3, 4]])
    assert fused[0][0] == 3


def test_rerank_keeps_the_highest_score(monkeypatch):
    monkeypatch.setattr(settings, "RERANK_K", 1)
    chunks = [_chunk(1, "alpha"), _chunk(2, "beta")]
    ranked = rerank("question", chunks, score_pairs=lambda question, texts: [0.1, 0.9])
    assert len(ranked) == 1
    assert ranked[0].chunk_id == 2
    assert ranked[0].score == pytest.approx(0.9)


def test_empty_retrieval_does_not_call_the_model():
    def fail(prompt: str) -> str:
        raise AssertionError(prompt)

    answer, indexes = generate_answer("What is the rate?", [], fail)
    assert answer == NOT_ENOUGH
    assert indexes == []


def test_cited_indexes_keep_only_real_chunks_and_drop_a_refusal():
    assert cited_indexes("Disclose the rate [1] and again [1]. Ignore [4].", 2) == [1]
    assert cited_indexes(f"{NOT_ENOUGH} [1]", 2) == []
