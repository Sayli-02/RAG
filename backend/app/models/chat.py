from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    String,
    Text,
    DateTime,
    Integer,
    Float,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class Conversation(Base):
    """Chat session initiated by a user."""

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), default="New Conversation", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """Individual user or assistant message within a conversation."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    conversation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # "user", "assistant"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    citations = relationship("Citation", back_populates="message", cascade="all, delete-orphan")


class Citation(Base):
    """Links an AI answer (message) back to the source document chunk."""

    __tablename__ = "citations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    message_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chunk_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("document_chunks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    relevance_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    message = relationship("Message", back_populates="citations")
    chunk = relationship("DocumentChunk", back_populates="citations")

