"""Export all SQLAlchemy models for easy import and Alembic discovery."""

from app.database.base import Base
from app.models.user import User
from app.models.document import Document, DocumentVersion, DocumentChunk
from app.models.chat import Conversation, Message, Citation
from app.models.comparison import ComparisonReport
from app.models.compliance import ComplianceChecklist, ComplianceRequirement
from app.models.query import SavedQuery
from app.models.evaluation import EvaluationRun

__all__ = [
    "Base",
    "User",
    "Document",
    "DocumentVersion",
    "DocumentChunk",
    "Conversation",
    "Message",
    "Citation",
    "ComparisonReport",
    "ComplianceChecklist",
    "ComplianceRequirement",
    "SavedQuery",
    "EvaluationRun",
]

