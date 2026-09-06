"""Chat Router - AI Conversation endpoints.

The backend controls the conversation flow. The frontend sends user input
and displays responses. No conversation logic lives in the frontend.

Guest Access:
- Guests can create sessions, send messages, and generate resumes
- Sessions are stored with user_id="anonymous" for guests
- Authentication is optional - only required for listing user's sessions
"""
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models.identity import User
from app.services.chat_service import ChatService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])

# Chat service singleton
_chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """Get or create the ChatService singleton."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service


# -----------------------------------------------------------------------
# Request/Response Models
# -----------------------------------------------------------------------


class CreateSessionRequest(BaseModel):
    """Request to create a new chat session."""
    title: Optional[str] = None


class SendMessageRequest(BaseModel):
    """Request to send a message in a chat session."""
    message: str = Field(..., min_length=1, max_length=10000)


class ChatMessageOut(BaseModel):
    """Chat message response."""
    id: str
    role: str
    content: str
    sequence: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatSessionOut(BaseModel):
    """Chat session response."""
    id: str
    title: Optional[str]
    status: str
    resume_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SendMessageResponse(BaseModel):
    """Response after sending a message."""
    success: bool
    message: str
    structured_data: Optional[dict] = None
    session_id: str


# -----------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------


@router.post("/sessions", response_model=ChatSessionOut)
async def create_session(
    request: CreateSessionRequest = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Create a new chat session.
    
    Guests can create sessions - they are stored with user_id="anonymous".
    Authenticated users get sessions linked to their account.
    """
    service = get_chat_service()
    user_id = current_user.id if current_user else "guest"
    title = request.title if request else None

    session = service.create_session(db, user_id=user_id, title=title)
    return session


@router.get("/sessions", response_model=List[ChatSessionOut])
async def list_sessions(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """List chat sessions.
    
    For authenticated users: returns their sessions.
    For guests: returns empty list (guest sessions are not persisted long-term).
    """
    service = get_chat_service()
    if not current_user:
        return []
    sessions = service.list_user_sessions(db, current_user.id)
    return sessions


@router.get("/sessions/{session_id}", response_model=ChatSessionOut)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Get a specific chat session.
    
    Accessible by anyone with the session ID (guest or authenticated).
    """
    service = get_chat_service()
    session = service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageOut])
async def get_messages(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Get all messages for a chat session.
    
    Accessible by anyone with the session ID (guest or authenticated).
    """
    service = get_chat_service()
    messages = service.get_session_messages(db, session_id)
    return [
        ChatMessageOut(
            id=str(m.id),
            role=m.role,
            content=m.content,
            sequence=m.sequence,
            created_at=m.created_at,
        )
        for m in messages
    ]


@router.post("/sessions/{session_id}/messages", response_model=SendMessageResponse)
async def send_message(
    session_id: str,
    request: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Send a message and get AI response.
    
    The backend controls the conversation flow. It:
    1. Saves the user message
    2. Builds context from conversation history
    3. Calls the AI provider
    4. Saves the assistant response
    5. Returns the response with any structured data
    
    Guests can send messages - no authentication required.
    """
    service = get_chat_service()
    result = await service.send_message(db, session_id, request.message)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Failed"))

    return SendMessageResponse(
        success=True,
        message=result["message"],
        structured_data=result.get("structured_data"),
        session_id=result["session_id"],
    )


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Delete a chat session.
    
    Accessible by anyone with the session ID (guest or authenticated).
    """
    service = get_chat_service()
    deleted = service.delete_session(db, session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted"}


@router.post("/sessions/{session_id}/close")
async def close_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Close a chat session.
    
    Accessible by anyone with the session ID (guest or authenticated).
    """
    service = get_chat_service()
    closed = service.close_session(db, session_id)
    if not closed:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session closed"}
