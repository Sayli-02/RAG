import re

from app.core.config import settings
from app.rag.retrieval import ScoredChunk

NOT_ENOUGH = "The documents do not contain enough information to answer this."


def build_prompt(question: str, chunks: list[ScoredChunk]) -> str:
    """Tell the model to stay inside the retrieved chunks and to cite them as [1], [2]."""
    blocks: list[str] = []
    for number, chunk in enumerate(chunks, start=1):
        page = chunk.page_number if chunk.page_number is not None else "?"
        blocks.append(f"[{number}] {chunk.title}, page {page}\n{chunk.text}")
    context = "\n\n".join(blocks)
    return (
        "You answer questions about financial regulations using only the context below.\n"
        f"If the context does not support an answer, reply exactly: {NOT_ENOUGH}\n"
        "Do not use outside knowledge. This is not legal advice.\n"
        "When you use a context block, cite it as [1] or [2], matching its number.\n\n"
        f"{context}\n\n"
        f"Question: {question}"
    )


def cited_indexes(answer: str, chunk_count: int) -> list[int]:
    """1-based chunk numbers the answer actually cited. A refusal cites nothing."""
    if NOT_ENOUGH in answer:
        return []
    found: list[int] = []
    for match in re.findall(r"\[(\d+)\]", answer):
        number = int(match)
        if 1 <= number <= chunk_count and number not in found:
            found.append(number)
    return found


def generate_answer(question: str, chunks: list[ScoredChunk], complete) -> tuple[str, list[int]]:
    """Return the answer text and the 1-based indexes of chunks it cited."""
    if not chunks:
        return NOT_ENOUGH, []
    answer = complete(build_prompt(question, chunks)).strip()
    return answer, cited_indexes(answer, len(chunks))


def complete_with_gemini(prompt: str) -> str:
    """One Gemini call. The API key stays in the environment."""
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set")
    from google import genai

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    response = client.models.generate_content(model=settings.GEMINI_MODEL, contents=prompt)
    text = (response.text or "").strip()
    if not text:
        raise ValueError("Gemini returned an empty answer")
    return text
