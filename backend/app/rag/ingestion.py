import logging
from dataclasses import dataclass

from app.core.config import settings
from app.database.session import SessionLocal
from app.models.document import Document, DocumentChunk
from app.rag.chunking import chunk_page
from app.rag.cleaning import clean_page_text, drop_repeated_lines
from app.rag.embeddings import embed_texts

logger = logging.getLogger(__name__)


@dataclass
class PageText:
    page_number: int
    text: str


@dataclass
class ChunkRecord:
    text: str
    page_number: int
    metadata: dict
    embedding: list[float]


def extract_pages(source: str | bytes) -> list[PageText]:
    """Read each page's text. Page numbers start at 1. A scanned page with no text is empty."""
    import fitz

    if isinstance(source, bytes):
        document = fitz.open(stream=source, filetype="pdf")
    else:
        document = fitz.open(source)
    try:
        return [
            PageText(page_number=index, text=page.get_text() or "")
            for index, page in enumerate(document, start=1)
        ]
    finally:
        document.close()


def _section_heading(text: str) -> str | None:
    first_line = text.split("\n", 1)[0].strip()
    if first_line and len(first_line) <= 80 and not first_line.endswith("."):
        return first_line
    return None


def build_chunk_records(source: str | bytes, embed=embed_texts) -> list[ChunkRecord]:
    """Clean, chunk, and embed a PDF. `embed` is replaceable in tests."""
    pages = extract_pages(source)
    cleaned_pages = drop_repeated_lines([clean_page_text(page.text) for page in pages])

    records: list[ChunkRecord] = []
    chunk_index = 0
    for page, cleaned in zip(pages, cleaned_pages):
        for text, start, end in chunk_page(cleaned, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP):
            records.append(
                ChunkRecord(
                    text=text,
                    page_number=page.page_number,
                    metadata={
                        "chunk_index": chunk_index,
                        "start_char": start,
                        "end_char": end,
                        "section_heading": _section_heading(text),
                    },
                    embedding=[],
                )
            )
            chunk_index += 1

    if not records:
        return []

    vectors = embed([record.text for record in records])
    if len(vectors) != len(records):
        raise ValueError("Embedder returned the wrong number of vectors")
    for record, vector in zip(records, vectors):
        if len(vector) != settings.VECTOR_DIMENSION:
            raise ValueError(
                f"Embedding has {len(vector)} dimensions, expected {settings.VECTOR_DIMENSION}"
            )
        record.embedding = vector
    return records


def ingest_document(document_id: int, version_id: int, file_path: str) -> None:
    """Store chunks for a saved PDF. Sets the document to indexed, or failed with a message."""
    db = SessionLocal()
    try:
        records = build_chunk_records(file_path)
        if not records:
            raise ValueError("No text could be extracted from this PDF")
        for record in records:
            db.add(
                DocumentChunk(
                    document_id=document_id,
                    version_id=version_id,
                    chunk_text=record.text,
                    page_number=record.page_number,
                    metadata_=record.metadata,
                    embedding=record.embedding,
                )
            )
        document = db.get(Document, document_id)
        if document is None:
            db.rollback()
            return
        document.status = "indexed"
        document.error_message = None
        db.commit()
    except Exception as exc:
        db.rollback()
        document = db.get(Document, document_id)
        if document is not None:
            document.status = "failed"
            document.error_message = str(exc)[:2000]
            db.commit()
        logger.exception("Ingestion failed for document %s", document_id)
    finally:
        db.close()
