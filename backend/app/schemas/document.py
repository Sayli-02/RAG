from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DocumentPublic(BaseModel):
    """Document fields returned by the list endpoint. Chunks stay on the detail route."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    authority: str
    category: str
    source_url: Optional[str] = None
    publication_date: Optional[date] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime


class VersionPublic(BaseModel):
    id: int
    version_number: str


class ChunkPublic(BaseModel):
    id: int
    page_number: Optional[int]
    chunk_text: str
    metadata: Optional[dict] = None


class DocumentDetail(DocumentPublic):
    versions: list[VersionPublic]
    chunks: list[ChunkPublic]


def to_document_detail(document) -> DocumentDetail:
    """Build the detail response. Chunks follow chunk_index, which is the reading order."""
    chunks = sorted(
        document.chunks,
        key=lambda chunk: (chunk.metadata_ or {}).get("chunk_index", chunk.id or 0),
    )
    return DocumentDetail(
        id=document.id,
        title=document.title,
        authority=document.authority,
        category=document.category,
        source_url=document.source_url,
        publication_date=document.publication_date,
        status=document.status,
        error_message=document.error_message,
        created_at=document.created_at,
        versions=[
            VersionPublic(id=version.id, version_number=version.version_number)
            for version in document.versions
        ],
        chunks=[
            ChunkPublic(
                id=chunk.id,
                page_number=chunk.page_number,
                chunk_text=chunk.chunk_text,
                metadata=chunk.metadata_,
            )
            for chunk in chunks
        ],
    )
