from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.assistant import citation_from_chunk
from app.schemas.research import CrossDocumentRequest, CrossDocumentResponse, SavedQueryPublic
from app.services.research_service import (
    DocumentNotIndexed,
    NeedTwoDocuments,
    UnknownDocument,
    ask_across_documents,
    list_queries,
)

router = APIRouter(prefix="/research", tags=["Research"])


@router.post("/cross-document", response_model=CrossDocumentResponse)
def cross_document(
    body: CrossDocumentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Answer from the selected indexed documents and save the question."""
    try:
        saved, answer, cited = ask_across_documents(
            db,
            current_user.id,
            body.question,
            body.document_ids,
        )
    except NeedTwoDocuments:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Choose at least two documents")
    except DocumentNotIndexed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Every document must be indexed")
    except UnknownDocument:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    return CrossDocumentResponse(
        query_id=saved.id,
        answer=answer,
        citations=[citation_from_chunk(chunk) for chunk in cited],
    )


@router.get("/queries", response_model=list[SavedQueryPublic])
def queries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_queries(db, current_user.id)
