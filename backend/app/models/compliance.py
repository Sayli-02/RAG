from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    String,
    Text,
    DateTime,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class ComplianceChecklist(Base):
    """Compliance checklists generated for a document."""

    __tablename__ = "compliance_checklists"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="compliance_checklists")
    document = relationship("Document", back_populates="compliance_checklists")
    requirements = relationship("ComplianceRequirement", back_populates="checklist", cascade="all, delete-orphan")


class ComplianceRequirement(Base):
    """Individual extracted compliance requirements and human review statuses."""

    __tablename__ = "compliance_requirements"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    checklist_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("compliance_checklists.id", ondelete="CASCADE"), nullable=False, index=True
    )
    requirement_text: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    authority: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    source_chunk_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("document_chunks.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), default="pending_review", nullable=False
    )  # "pending_review", "reviewed", "not_applicable"
    reviewer_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
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
    checklist = relationship("ComplianceChecklist", back_populates="requirements")
    source_chunk = relationship("DocumentChunk")

