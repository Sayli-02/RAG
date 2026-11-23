from datetime import datetime, timezone
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class User(Base):
    """User account model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="user", nullable=False)  # "user", "admin"
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
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    comparison_reports = relationship("ComparisonReport", back_populates="user", cascade="all, delete-orphan")
    compliance_checklists = relationship("ComplianceChecklist", back_populates="user", cascade="all, delete-orphan")
    saved_queries = relationship("SavedQuery", back_populates="user", cascade="all, delete-orphan")

