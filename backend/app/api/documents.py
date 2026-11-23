from datetime import date

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.rag.ingestion import ingest_document
from app.schemas.document import DocumentDetail, DocumentPublic, to_document_detail
from app.services.document_service import (
    AUTHORITIES,
    create_document,
    delete_document,
    get_owned_document,
    list_documents,
    save_pdf,
    validate_pdf,
)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentPublic, status_code=status.HTTP_201_CREATED)
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    authority: str = Form(...),
    category: str = Form(...),
    publication_date: date | None = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save a PDF and index it after this response. Poll GET /documents/{id} for status."""
    title = title.strip()
    category = category.strip()
    if not title or not category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title and category are required")
    if authority not in AUTHORITIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="authority must be RBI, SEBI, NPCI, or OTHER",
        )

    data = file.file.read()
    try:
        validate_pdf(file.filename, data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    path = save_pdf(data)
    try:
        document, version = create_document(
            db,
            user_id=current_user.id,
            title=title,
            authority=authority,
            category=category,
            publication_date=publication_date,
            file_path=str(path),
        )
    except Exception:
        path.unlink(missing_ok=True)
        raise

    background_tasks.add_task(ingest_document, document.id, version.id, str(path))
    return document


@router.get("", response_model=list[DocumentPublic])
def list_my_documents(
    authority: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    q: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List the current user's documents. Filter by authority, status, or a title search."""
    return list_documents(
        db,
        current_user.id,
        authority=authority,
        status=status_filter,
        q=q,
    )


@router.get("/{document_id}", response_model=DocumentDetail)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Metadata, version, and chunks with page numbers. Other users' documents look missing."""
    document = get_owned_document(db, current_user.id, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return to_document_detail(document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete the document, its chunks, and the saved PDF."""
    document = get_owned_document(db, current_user.id, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    delete_document(db, document)
