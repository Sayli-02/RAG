import re

from app.rag.generation import NOT_ENOUGH


def hit_and_reciprocal(retrieved_pages: list[int | None], expected_page: int, k: int) -> tuple[float, float]:
    """1 and 1/rank when the expected page is inside the top k, otherwise 0 and 0."""
    window = [page for page in retrieved_pages[:k] if page is not None]
    if expected_page not in window:
        return 0.0, 0.0
    rank = window.index(expected_page) + 1
    return 1.0, 1.0 / rank


def aggregate_retriever(hits: list[tuple[int, list[int | None]]], k: int) -> dict:
    """Average recall@k and mean reciprocal rank. An empty case list scores 0."""
    if not hits:
        return {"recall_at_k": 0.0, "mrr": 0.0}
    recall_total = 0.0
    rr_total = 0.0
    for expected, pages in hits:
        recall, reciprocal = hit_and_reciprocal(pages, expected, k)
        recall_total += recall
        rr_total += reciprocal
    count = len(hits)
    return {"recall_at_k": recall_total / count, "mrr": rr_total / count}


def lexical_faithfulness(answer: str, context: str) -> float:
    """Share of answer words (longer than 3 letters) that appear in the retrieved text.

    The refusal sentence scores 1. This is a word-overlap stand-in, not an LLM judge.
    """
    if answer.strip() == NOT_ENOUGH:
        return 1.0
    words = [word for word in re.findall(r"[a-z0-9]+", answer.lower()) if len(word) > 3]
    if not words:
        return 0.0
    haystack = context.lower()
    found = sum(1 for word in words if word in haystack)
    return found / len(words)
