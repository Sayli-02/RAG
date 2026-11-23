from datetime import datetime, timezone
from typing import Optional, Any
from sqlalchemy import (
    Text,
    DateTime,
    Integer,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class ComparisonReport(Base):
    """Saved regulatory change-detection reports comparing two versions."""

    __tablename__ = "comparison_reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version_a_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version_b_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    report_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="comparison_reports")
    version_a = relationship("DocumentVersion", foreign_keys=[version_a_id])
    version_b = relationship("DocumentVersion", foreign_keys=[version_b_id])

