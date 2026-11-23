from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.schemas.assistant import CitationPublic


class CrossDocumentRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    document_ids: list[int] = Field(min_length=2)

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Question is required")
        return value


class CrossDocumentResponse(BaseModel):
    query_id: int
    answer: str
    citations: list[CitationPublic]


class SavedQueryPublic(BaseModel):
    id: int
    query_text: str
    created_at: datetime
