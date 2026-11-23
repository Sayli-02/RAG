from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.chat import Citation, Conversation, Message
from app.models.document import DocumentChunk
from app.rag.embeddings import embed_texts
from app.rag.generation import complete_with_gemini, generate_answer
from app.rag.retrieval import ScoredChunk, hybrid_search
from app.schemas.assistant import CitationPublic


class ConversationNotFound(Exception):
    """The conversation is missing or belongs to another user."""


def answer_question(
    db: Session,
    user_id: int,
    question: str,
    conversation_id: int | None,
) -> tuple[Conversation, str, list[ScoredChunk]]:
    """Retrieve, generate, and store one turn. Returns the conversation, answer, and cited chunks."""
    conversation = _conversation_for_turn(db, user_id, question, conversation_id)
    db.add(Message(conversation_id=conversation.id, role="user", content=question))
    db.flush()

    query_vector = embed_texts([question])[0]
    retrieved = hybrid_search(db, user_id, question, query_vector)
    answer, indexes = generate_answer(question, retrieved, complete_with_gemini)
    cited = [retrieved[index - 1] for index in indexes]

    message = Message(conversation_id=conversation.id, role="assistant", content=answer)
    db.add(message)
    db.flush()
    for chunk in cited:
        db.add(
            Citation(
                message_id=message.id,
                chunk_id=chunk.chunk_id,
                relevance_score=chunk.score,
            )
        )
    db.commit()
    db.refresh(conversation)
    return conversation, answer, cited


def list_conversations(db: Session, user_id: int) -> list[Conversation]:
    stmt = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def get_conversation(db: Session, user_id: int, conversation_id: int) -> Conversation | None:
    stmt = (
        select(Conversation)
        .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
        .options(
            selectinload(Conversation.messages)
            .selectinload(Message.citations)
            .selectinload(Citation.chunk)
            .selectinload(DocumentChunk.document)
        )
    )
    return db.scalars(stmt).first()


def citation_from_row(citation: Citation) -> CitationPublic:
    chunk = citation.chunk
    document = chunk.document
    heading = (chunk.metadata_ or {}).get("section_heading") or None
    return CitationPublic(
        document_title=document.title,
        authority=document.authority,
        page_number=chunk.page_number,
        section=heading,
        excerpt=chunk.chunk_text,
        relevance_score=citation.relevance_score,
    )


def _conversation_for_turn(
    db: Session,
    user_id: int,
    question: str,
    conversation_id: int | None,
) -> Conversation:
    if conversation_id is None:
        conversation = Conversation(user_id=user_id, title=question[:80])
        db.add(conversation)
        db.flush()
        return conversation
    conversation = db.scalars(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
    ).first()
    if conversation is None:
        raise ConversationNotFound
    return conversation
