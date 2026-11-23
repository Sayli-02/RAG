from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.comparison import CompareRequest, ReportDetail, ReportPublic, to_report_detail, to_report_public
from app.services.comparison_service import (
    DocumentNotIndexed,
    SameDocument,
    UnknownDocument,
    UnknownReport,
    compare_documents,
    get_report,
    list_reports,
)

router = APIRouter(prefix="/comparison", tags=["Comparison"])


@router.post("/compare", response_model=ReportDetail, status_code=status.HTTP_201_CREATED)
def compare(
    body: CompareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Diff the latest indexed versions of two of the current user's documents."""
    try:
        report = compare_documents(db, current_user.id, body.document_a_id, body.document_b_id)
    except SameDocument:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Choose two different documents")
    except DocumentNotIndexed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Both documents must be indexed")
    except UnknownDocument:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return to_report_detail(report)


@router.get("/reports", response_model=list[ReportPublic])
def reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return [to_report_public(report) for report in list_reports(db, current_user.id)]


@router.get("/reports/{report_id}", response_model=ReportDetail)
def read_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        report = get_report(db, current_user.id, report_id)
    except UnknownReport:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return to_report_detail(report)
