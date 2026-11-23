import json
import math
import re
from difflib import SequenceMatcher

from pydantic import BaseModel, ValidationError

UNCHANGED_RATIO = 0.92
PAIR_TEXT_RATIO = 0.4
PAIR_COSINE = 0.75


def cosine(left: list[float] | None, right: list[float] | None) -> float:
    """Cosine of two embeddings. Missing or empty vectors score 0."""
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def text_ratio(left: str, right: str) -> float:
    return SequenceMatcher(None, left, right).ratio()


def _pair_score(older: dict, newer: dict) -> tuple[float, float, float]:
    ratio = text_ratio(older["text"], newer["text"])
    similarity = cosine(older.get("embedding"), newer.get("embedding"))
    page_bonus = 0.05 if older.get("page") and older.get("page") == newer.get("page") else 0.0
    if older.get("embedding") and newer.get("embedding"):
        score = 0.45 * ratio + 0.55 * similarity + page_bonus
    else:
        score = ratio + page_bonus
    return score, ratio, similarity


def build_diff(older: list[dict], newer: list[dict]) -> dict:
    """Pair chunks and label them added, removed, modified, or unchanged.

    Each chunk dict needs text, and may include page, chunk_id, and embedding.
    A high cosine can pair a rewritten sentence that a word-for-word diff would miss.
    """
    unused_new = set(range(len(newer)))
    used_old: set[int] = set()
    modified: list[dict] = []
    unchanged = 0

    for old_index, old in enumerate(older):
        best_index = None
        best_score = -1.0
        best_ratio = 0.0
        best_similarity = 0.0
        for new_index in unused_new:
            score, ratio, similarity = _pair_score(old, newer[new_index])
            if score > best_score:
                best_index = new_index
                best_score = score
                best_ratio = ratio
                best_similarity = similarity
        if best_index is None or (best_ratio < PAIR_TEXT_RATIO and best_similarity < PAIR_COSINE):
            continue
        unused_new.remove(best_index)
        used_old.add(old_index)
        new = newer[best_index]
        if best_ratio >= UNCHANGED_RATIO:
            unchanged += 1
            continue
        modified.append(
            {
                "page": new.get("page"),
                "before": old["text"],
                "after": new["text"],
                "chunk_id_before": old.get("chunk_id"),
                "chunk_id_after": new.get("chunk_id"),
            }
        )

    removed = [
        {"page": chunk.get("page"), "text": chunk["text"], "chunk_id": chunk.get("chunk_id")}
        for index, chunk in enumerate(older)
        if index not in used_old
    ]
    added = [
        {"page": newer[index].get("page"), "text": newer[index]["text"], "chunk_id": newer[index].get("chunk_id")}
        for index in sorted(unused_new)
    ]
    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "unchanged_count": unchanged,
        "affected_requirements": [],
    }


def count_summary(diff: dict) -> str:
    return (
        f"{len(diff['added'])} added, {len(diff['removed'])} removed, "
        f"{len(diff['modified'])} modified."
    )


class _SummaryPayload(BaseModel):
    summary: str
    affected_requirements: list[str] = []


def summarize_diff(diff: dict, complete=None) -> tuple[str, list[str]]:
    """Ask for a JSON summary. A missing or invalid reply falls back to counts."""
    fallback = count_summary(diff)
    if complete is None:
        return fallback, []
    preview = {"added": diff["added"], "removed": diff["removed"], "modified": diff["modified"]}
    prompt = (
        "You summarize a regulatory change report. Reply with JSON only, no markdown.\n"
        '{"summary": "one short paragraph", "affected_requirements": ["requirement that may have changed"]}\n'
        "Use only the changes below. This is not legal advice.\n\n"
        + json.dumps(preview)
    )
    try:
        raw = complete(prompt)
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        payload = _SummaryPayload.model_validate_json(match.group(0) if match else raw)
    except (ValueError, ValidationError, AttributeError, TypeError):
        return fallback, []
    summary = payload.summary.strip() or fallback
    return summary, payload.affected_requirements
