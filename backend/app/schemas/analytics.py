from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class FrequentQuery(BaseModel):
    query_text: str
    count: int


class RecentDocument(BaseModel):
    id: int
    title: str
    authority: str
    status: str
    updated_at: datetime


class RecentComparison(BaseModel):
    id: int
    summary: Optional[str] = None
    document_a_title: str
    document_b_title: str
    created_at: datetime


class ReviewCounts(BaseModel):
    pending_review: int
    reviewed: int
    not_applicable: int


class AnalyticsSummary(BaseModel):
    documents_total: int
    documents_indexed: int
    by_authority: dict[str, int]
    by_status: dict[str, int]
    recent_documents: list[RecentDocument]
    frequent_queries: list[FrequentQuery]
    recent_comparisons: list[RecentComparison]
    review: ReviewCounts


class EvaluationRunPublic(BaseModel):
    id: int
    run_name: str
    dataset_name: str
    metrics_json: dict[str, Any]
    created_at: datetime
