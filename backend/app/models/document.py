from datetime import datetime, date, timezone
from typing import Optional, Any
from sqlalchemy import (
    String,
    Text,
    Date,
    DateTime,
    Integer,
    ForeignKey,
    Index,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.database.base import Base
from app.core.config import settings


class Document(Base):
    """Regulatory document metadata."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    authority: Mapped[str] = mapped_column(String(50), nullable=False)  # "RBI", "SEBI", "NPCI", "OTHER"
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "Master Direction", "Circular"
    source_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    publication_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    uploaded_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default="uploaded", nullable=False
    )  # "uploaded", "processing", "indexed", "failed"
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    compliance_checklists = relationship("ComplianceChecklist", back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_documents_authority_category_status", "authority", "category", "status"),
    )


class DocumentVersion(Base):
    """Document version management for change tracking and comparison."""

    __tablename__ = "document_versions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version_number: Mapped[str] = mapped_column(String(50), default="1.0", nullable=False)
    effective_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    parent_version_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("document_versions.id", ondelete="SET NULL"), nullable=True
    )
    file_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    document = relationship("Document", back_populates="versions")
    chunks = relationship("DocumentChunk", back_populates="version", cascade="all, delete-orphan")
    parent_version = relationship("DocumentVersion", remote_side=[id])


class DocumentChunk(Base):
    """Extracted text chunks and embedding vectors for RAG."""

    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=True, index=True
    )
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    metadata_: Mapped[Optional[dict[str, Any]]] = mapped_column("metadata", JSON, nullable=True)
    embedding = mapped_column(Vector(settings.VECTOR_DIMENSION), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    document = relationship("Document", back_populates="chunks")
    version = relationship("DocumentVersion", back_populates="chunks")
    citations = relationship("Citation", back_populates="chunk", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_document_chunks_doc_version", "document_id", "version_id"),
    )

