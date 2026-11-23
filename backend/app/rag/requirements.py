import json
import re

from pydantic import BaseModel, ValidationError

OBLIGATION = re.compile(r"\b(must|shall|required to|is required)\b", re.IGNORECASE)


class _RequirementItem(BaseModel):
    requirement_text: str
    category: str = "obligation"
    chunk_index: int


class _RequirementPayload(BaseModel):
    requirements: list[_RequirementItem]


def heuristic_requirements(chunks: list[dict]) -> list[dict]:
    """Pull obligation sentences when no model is available.

    A chunk dict needs text and may include chunk_id.
    """
    found: list[dict] = []
    for chunk in chunks:
        sentences = re.split(r"(?<=[.!?])\s+", chunk["text"])
        for sentence in sentences:
            text = sentence.strip()
            if len(text) < 20 or not OBLIGATION.search(text):
                continue
            found.append(
                {
                    "requirement_text": text,
                    "category": "obligation",
                    "chunk_id": chunk.get("chunk_id"),
                }
            )
    return found[:30]


def extract_requirements(chunks: list[dict], complete=None) -> list[dict]:
    """Return requirement dicts. A bad model reply falls back to the obligation sentences."""
    if complete is None:
        return heuristic_requirements(chunks)
    numbered = []
    for index, chunk in enumerate(chunks, start=1):
        numbered.append(f"[{index}] {chunk['text']}")
    prompt = (
        "Extract compliance requirements from these regulatory chunks. Reply with JSON only.\n"
        '{"requirements": [{"requirement_text": "what a firm must do", "category": "disclosure", "chunk_index": 1}]}\n'
        "chunk_index is the number in brackets. Use only the text below. This is not legal advice.\n\n"
        + "\n\n".join(numbered)
    )
    try:
        raw = complete(prompt)
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        payload = _RequirementPayload.model_validate_json(match.group(0) if match else raw)
    except (ValueError, ValidationError, AttributeError, TypeError):
        return heuristic_requirements(chunks)
    parsed: list[dict] = []
    for item in payload.requirements:
        if item.chunk_index < 1 or item.chunk_index > len(chunks):
            continue
        text = item.requirement_text.strip()
        if not text:
            continue
        parsed.append(
            {
                "requirement_text": text,
                "category": item.category.strip() or "obligation",
                "chunk_id": chunks[item.chunk_index - 1].get("chunk_id"),
            }
        )
    return parsed or heuristic_requirements(chunks)
