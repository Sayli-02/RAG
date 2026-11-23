from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.analytics import EvaluationRunPublic
from app.services.evaluation_service import latest_run, run_evaluation

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


@router.post("/run", response_model=EvaluationRunPublic, status_code=status.HTTP_201_CREATED)
def run(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Score the sample questions against this user's indexed documents and store the run."""
    try:
        return run_evaluation(db, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))


@router.get("/latest", response_model=EvaluationRunPublic | None)
def latest(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return latest_run(db)
