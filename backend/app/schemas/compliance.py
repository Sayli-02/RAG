from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ExtractRequest(BaseModel):
    document_id: int


class RequirementPublic(BaseModel):
    id: int
    requirement_text: str
    category: Optional[str] = None
    authority: Optional[str] = None
    page_number: Optional[int] = None
    status: str
    reviewer_notes: Optional[str] = None


class ChecklistPublic(BaseModel):
    id: int
    title: str
    document_id: int
    document_title: str
    created_at: datetime


class ChecklistDetail(ChecklistPublic):
    requirements: list[RequirementPublic]


class ReviewUpdate(BaseModel):
    status: Literal["pending_review", "reviewed", "not_applicable"]
    reviewer_notes: Optional[str] = Field(default=None, max_length=2000)


def requirement_public(requirement) -> RequirementPublic:
    page = requirement.source_chunk.page_number if requirement.source_chunk is not None else None
    return RequirementPublic(
        id=requirement.id,
        requirement_text=requirement.requirement_text,
        category=requirement.category,
        authority=requirement.authority,
        page_number=page,
        status=requirement.status,
        reviewer_notes=requirement.reviewer_notes,
    )


def checklist_public(checklist) -> ChecklistPublic:
    return ChecklistPublic(
        id=checklist.id,
        title=checklist.title,
        document_id=checklist.document_id,
        document_title=checklist.document.title,
        created_at=checklist.created_at,
    )


def checklist_detail(checklist) -> ChecklistDetail:
    public = checklist_public(checklist)
    return ChecklistDetail(
        **public.model_dump(),
        requirements=[requirement_public(item) for item in checklist.requirements],
    )
