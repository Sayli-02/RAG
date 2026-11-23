from datetime import datetime, timezone
from sqlalchemy import (
    Text,
    DateTime,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class SavedQuery(Base):
    """Saved research queries for a user."""

    __tablename__ = "saved_queries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="saved_queries")

