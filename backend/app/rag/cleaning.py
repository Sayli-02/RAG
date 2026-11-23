import re
from collections import Counter


def clean_page_text(text: str) -> str:
    """Turn one PDF page into paragraphs. Join words split by a line-break hyphen."""
    text = text.replace("\x00", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def drop_repeated_lines(pages: list[str]) -> list[str]:
    """Drop a short line that shows up on every non-empty page (running header or footer)."""
    nonempty = [page for page in pages if page.strip()]
    if len(nonempty) < 3:
        return pages

    counts: Counter[str] = Counter()
    for page in nonempty:
        counts.update({line for line in page.split("\n") if line.strip()})
    repeated = {line for line, count in counts.items() if count == len(nonempty) and len(line) <= 80}
    if not repeated:
        return pages

    cleaned: list[str] = []
    for page in pages:
        kept = [line for line in page.split("\n") if line not in repeated]
        cleaned.append("\n".join(kept).strip())
    return cleaned
