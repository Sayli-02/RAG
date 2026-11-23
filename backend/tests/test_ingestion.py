import fitz

from app.core.config import settings
from app.rag.chunking import chunk_page
from app.rag.cleaning import clean_page_text, drop_repeated_lines
from app.rag.ingestion import build_chunk_records


def test_clean_page_joins_hyphenated_line_break():
    cleaned = clean_page_text("regula-\ntion   applies\r\n\r\n\r\nto banks")
    assert "regulation applies" in cleaned
    assert "\n\n" in cleaned
    assert "to banks" in cleaned


def test_drop_repeated_header_keeps_body():
    pages = [
        "Reserve Bank of India\nBody one",
        "Reserve Bank of India\nBody two",
        "Reserve Bank of India\nBody three",
    ]
    cleaned = drop_repeated_lines(pages)
    assert cleaned[0] == "Body one"
    assert "Reserve Bank of India" not in cleaned[1]
    assert "Body three" in cleaned[2]


def test_chunk_page_overlaps_and_stays_in_one_page():
    text = " ".join(f"word{i}" for i in range(400))
    chunks = chunk_page(text, size=500, overlap=50)
    assert len(chunks) >= 3
    assert chunks[1][1] < chunks[0][2]
    assert all(piece in text for piece, _, _ in chunks)


def test_build_chunk_records_keeps_page_numbers():
    document = fitz.open()
    for marker in ("PAGE-ONE-MARKER alpha", "PAGE-TWO-MARKER beta"):
        page = document.new_page()
        page.insert_text((72, 72), marker)
    pdf = document.tobytes()
    document.close()

    def fake_embed(texts: list[str]) -> list[list[float]]:
        return [[float(index)] + [0.0] * (settings.VECTOR_DIMENSION - 1) for index, _ in enumerate(texts)]

    records = build_chunk_records(pdf, embed=fake_embed)
    by_page = {record.page_number: record.text for record in records}
    assert "PAGE-ONE-MARKER" in by_page[1]
    assert "PAGE-TWO-MARKER" in by_page[2]
    assert "PAGE-TWO-MARKER" not in by_page[1]
    assert len(records[0].embedding) == settings.VECTOR_DIMENSION
    assert records[0].metadata["chunk_index"] == 0


def test_build_chunk_records_empty_pdf_returns_nothing():
    document = fitz.open()
    document.new_page()
    pdf = document.tobytes()
    document.close()
    assert build_chunk_records(pdf, embed=lambda texts: []) == []
