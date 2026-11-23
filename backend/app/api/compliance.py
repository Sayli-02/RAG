from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.compliance import (
    ChecklistDetail,
    ChecklistPublic,
    ExtractRequest,
    RequirementPublic,
    ReviewUpdate,
    checklist_detail,
    checklist_public,
    requirement_public,
)
from app.services.compliance_service import (
    BadReviewStatus,
    DocumentNotIndexed,
    UnknownChecklist,
    UnknownDocument,
    UnknownRequirement,
    checklist_csv,
    extract_checklist,
    get_checklist,
    list_checklists,
    update_requirement,
)

router = APIRouter(prefix="/compliance", tags=["Compliance"])


@router.post("/extract", response_model=ChecklistDetail, status_code=status.HTTP_201_CREATED)
def extract(
    body: ExtractRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Extract a checklist from one indexed document the current user owns."""
    try:
        checklist = extract_checklist(db, current_user.id, body.document_id)
    except DocumentNotIndexed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Document must be indexed")
    except UnknownDocument:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return checklist_detail(checklist)


@router.get("/checklists", response_model=list[ChecklistPublic])
def checklists(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = []
    for checklist in list_checklists(db, current_user.id):
        checklist.document
        rows.append(checklist_public(checklist))
    return rows


@router.get("/checklists/{checklist_id}", response_model=ChecklistDetail)
def read_checklist(
    checklist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        checklist = get_checklist(db, current_user.id, checklist_id)
    except UnknownChecklist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist not found")
    return checklist_detail(checklist)


@router.get("/checklists/{checklist_id}/export")
def export_checklist(
    checklist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        checklist = get_checklist(db, current_user.id, checklist_id)
    except UnknownChecklist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist not found")
    return Response(
        content=checklist_csv(checklist),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="checklist-{checklist.id}.csv"'},
    )


@router.patch("/requirements/{requirement_id}", response_model=RequirementPublic)
def review_requirement(
    requirement_id: int,
    body: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        requirement = update_requirement(
            db,
            current_user.id,
            requirement_id,
            body.status,
            body.reviewer_notes,
        )
    except BadReviewStatus:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown review status")
    except UnknownRequirement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Requirement not found")
    return requirement_public(requirement)
