from datetime import datetime, timezone
from typing import Any
from sqlalchemy import (
    String,
    DateTime,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class EvaluationRun(Base):
    """RAGAS and retrieval evaluation run results."""

    __tablename__ = "evaluation_runs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    run_name: Mapped[str] = mapped_column(String(255), nullable=False)
    dataset_name: Mapped[str] = mapped_column(String(255), nullable=False)
    metrics_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

