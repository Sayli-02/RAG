from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.rag.retrieval import ScoredChunk


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    conversation_id: Optional[int] = None

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Question is required")
        return value


class CitationPublic(BaseModel):
    document_title: str
    authority: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    excerpt: str
    relevance_score: Optional[float] = None


class AskResponse(BaseModel):
    conversation_id: int
    answer: str
    citations: list[CitationPublic]


class ConversationPublic(BaseModel):
    id: int
    title: str
    created_at: datetime


class MessagePublic(BaseModel):
    id: int
    role: str
    content: str
    citations: list[CitationPublic]


class ConversationDetail(ConversationPublic):
    messages: list[MessagePublic]


def citation_from_chunk(chunk: ScoredChunk) -> CitationPublic:
    return CitationPublic(
        document_title=chunk.title,
        authority=chunk.authority,
        page_number=chunk.page_number,
        section=chunk.section_heading,
        excerpt=chunk.text,
        relevance_score=chunk.score,
    )
