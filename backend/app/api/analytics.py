from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.analytics import AnalyticsSummary
from app.services.analytics_service import analytics_summary

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Counts for the current user's documents, comparisons, queries, and reviews."""
    return analytics_summary(db, current_user.id)
