from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class CompareRequest(BaseModel):
    document_a_id: int
    document_b_id: int


class ReportPublic(BaseModel):
    id: int
    summary: Optional[str] = None
    created_at: datetime
    document_a_title: str
    document_b_title: str
    version_a_id: int
    version_b_id: int


class ReportDetail(ReportPublic):
    report_json: dict[str, Any]


def to_report_public(report) -> ReportPublic:
    return ReportPublic(
        id=report.id,
        summary=report.summary,
        created_at=report.created_at,
        document_a_title=report.version_a.document.title,
        document_b_title=report.version_b.document.title,
        version_a_id=report.version_a_id,
        version_b_id=report.version_b_id,
    )


def to_report_detail(report) -> ReportDetail:
    public = to_report_public(report)
    return ReportDetail(**public.model_dump(), report_json=report.report_json)
