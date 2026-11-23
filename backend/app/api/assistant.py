from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.assistant import (
    AskRequest,
    AskResponse,
    ConversationDetail,
    ConversationPublic,
    MessagePublic,
    citation_from_chunk,
)
from app.services.assistant_service import (
    ConversationNotFound,
    answer_question,
    citation_from_row,
    get_conversation,
    list_conversations,
)

router = APIRouter(prefix="/assistant", tags=["Assistant"])


@router.post("/ask", response_model=AskResponse)
def ask(
    body: AskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Answer from the current user's indexed documents and store the turn."""
    try:
        conversation, answer, cited = answer_question(
            db,
            current_user.id,
            body.question,
            body.conversation_id,
        )
    except ConversationNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    return AskResponse(
        conversation_id=conversation.id,
        answer=answer,
        citations=[citation_from_chunk(chunk) for chunk in cited],
    )


@router.get("/conversations", response_model=list[ConversationPublic])
def list_my_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_conversations(db, current_user.id)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def read_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = get_conversation(db, current_user.id, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    messages = sorted(conversation.messages, key=lambda message: (message.created_at, message.id))
    return ConversationDetail(
        id=conversation.id,
        title=conversation.title,
        created_at=conversation.created_at,
        messages=[
            MessagePublic(
                id=message.id,
                role=message.role,
                content=message.content,
                citations=[citation_from_row(citation) for citation in message.citations],
            )
            for message in messages
        ],
    )
