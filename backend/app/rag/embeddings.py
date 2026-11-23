from app.core.config import settings

_model = None


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed texts with the configured Hugging Face model. Vectors are unit length."""
    if not texts:
        return []
    vectors = _get_model().encode(texts, normalize_embeddings=True)
    result: list[list[float]] = []
    for vector in vectors:
        values = [float(item) for item in vector]
        if len(values) != settings.VECTOR_DIMENSION:
            raise ValueError(
                f"Embedding model returned {len(values)} dimensions, "
                f"expected {settings.VECTOR_DIMENSION}"
            )
        result.append(values)
    return result


def _get_model():
    """Load the model on first use so tests that inject a fake embedder never download it."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _model
