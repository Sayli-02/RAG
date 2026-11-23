def chunk_page(text: str, size: int, overlap: int) -> list[tuple[str, int, int]]:
    """Split one page into windows of about `size` characters.

    Each item is (text, start_char, end_char) within this page. Pages are never merged,
    so the caller keeps a single page number on every chunk.
    """
    text = text.strip()
    if not text:
        return []
    if size < 1:
        raise ValueError("Chunk size must be at least 1")
    if overlap < 0 or overlap >= size:
        overlap = 0
    if len(text) <= size:
        return [(text, 0, len(text))]

    chunks: list[tuple[str, int, int]] = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            break_at = text.rfind("\n", start + 1, end)
            if break_at == -1:
                break_at = text.rfind(" ", start + 1, end)
            if break_at > start:
                end = break_at
        piece = text[start:end].strip()
        if piece:
            chunks.append((piece, start, end))
        if end >= len(text):
            break
        next_start = end - overlap
        if next_start <= start:
            next_start = end
        start = next_start
    return chunks
