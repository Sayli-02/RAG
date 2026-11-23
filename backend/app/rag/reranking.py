from dataclasses import replace

from app.core.config import settings
from app.rag.retrieval import ScoredChunk

_model = None


def rerank(question: str, chunks: list[ScoredChunk], score_pairs=None) -> list[ScoredChunk]:
    """Score each question-and-chunk pair and keep the best RERANK_K."""
    if not chunks:
        return []
    if score_pairs is None:
        score_pairs = _cross_encoder_scores
    scores = score_pairs(question, [chunk.text for chunk in chunks])
    ranked = [replace(chunk, score=float(score)) for chunk, score in zip(chunks, scores)]
    ranked.sort(key=lambda chunk: chunk.score, reverse=True)
    return ranked[: settings.RERANK_K]


def _cross_encoder_scores(question: str, texts: list[str]) -> list[float]:
    """Load the cross-encoder on first use. Tests pass score_pairs and never reach this."""
    global _model
    if _model is None:
        from sentence_transformers import CrossEncoder

        _model = CrossEncoder(settings.RERANKER_MODEL)
    raw = _model.predict([(question, text) for text in texts])
    return [float(score) for score in raw]
