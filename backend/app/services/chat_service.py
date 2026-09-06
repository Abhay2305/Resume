"""Chat Service - Manages AI conversation sessions.

The backend controls the conversation flow. The frontend is a thin renderer
that sends user input and displays responses.
"""
import json
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.conversation import ChatSession, ChatMessage
from app.services.ai_service import UniversalAIService, get_ai_service
from app.services.prompt_intelligence_v2.builder import PromptBuilder as PromptBuilderV2
from app.services.prompt_intelligence_v2.types import PromptRequest

logger = logging.getLogger(__name__)


class ChatService:
    """Manages AI conversation sessions with context persistence."""

    def __init__(
        self,
        provider: Optional[UniversalAIService] = None,
        prompt_builder_v2: Optional[PromptBuilderV2] = None,
    ):
        self.provider = provider or get_ai_service()
        self._prompt_builder_v2 = prompt_builder_v2 or PromptBuilderV2()

    def create_session(
        self, db: Session, user_id: Optional[str] = None, title: Optional[str] = None
    ) -> ChatSession:
        """Create a new chat session."""
        session = ChatSession(
            user_id=user_id or "guest",
            title=title or "New Resume Conversation",
            status="active",
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def get_session(self, db: Session, session_id: str) -> Optional[ChatSession]:
        """Get a chat session by ID."""
        return db.query(ChatSession).filter(ChatSession.id == session_id).first()

    def get_session_messages(self, db: Session, session_id: str) -> List[ChatMessage]:
        """Get all messages for a session, ordered by sequence."""
        return (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.sequence)
            .all()
        )

    def list_user_sessions(
        self, db: Session, user_id: str, limit: int = 50
    ) -> List[ChatSession]:
        """List all sessions for a user."""
        return (
            db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .order_by(ChatSession.created_at.desc())
            .limit(limit)
            .all()
        )

    async def send_message(
        self, db: Session, session_id: str, user_message: str
    ) -> Dict[str, Any]:
        """Send a user message and get AI response.

        This is the core method. It:
        1. Saves the user message
        2. Builds context from conversation history
        3. Calls the AI provider (universal service routes internally)
        4. Saves the assistant response
        5. Returns the response with any structured data
        """
        session = self.get_session(db, session_id)
        if not session:
            return {"success": False, "error": "Session not found"}

        # Get existing messages for context
        existing_messages = self.get_session_messages(db, session_id)
        next_sequence = len(existing_messages) + 1

        # Save user message
        user_msg = ChatMessage(
            session_id=session_id,
            role="user",
            content=user_message,
            sequence=next_sequence,
        )
        db.add(user_msg)
        db.commit()

        # Build messages for AI
        messages = self._build_messages(existing_messages, user_message, db=db)

        # Call AI provider (universal service handles routing)
        try:
            response = await self.provider.generate(messages)
            assistant_content = response.content
        except Exception as e:
            logger.error("AI provider error: %s", str(e), exc_info=True)
            assistant_content = (
                "I apologize, but I encountered an error processing your request. "
                "Please try again or type 'generate' if you'd like me to create your resume with the information so far."
            )

        # Save assistant message
        assistant_msg = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=assistant_content,
            sequence=next_sequence + 1,
        )
        db.add(assistant_msg)
        db.commit()

        # Check if AI response contains structured data
        structured_data = self._extract_structured_data(assistant_content)

        # Run validation gate for resume generation requests
        prompt_type = self._detect_prompt_type(user_message)
        validation_result = None
        if prompt_type == "resume_generation" and structured_data:
            validation_result = self._validate_resume_output(
                structured_data, user_message, db=db
            )

        # Update session title if this is the first exchange
        if len(existing_messages) == 0 and not session.title:
            session.title = self._generate_title(user_message)
            db.commit()

        result = {
            "success": True,
            "message": assistant_content,
            "structured_data": structured_data,
            "session_id": session_id,
        }
        if validation_result is not None:
            result["validation"] = validation_result
        return result

    _RESUME_KEYWORDS = frozenset({
        "resume", "cv", "create", "generate", "build", "write",
        "update", "improve", "tailor", "optimize", "rewrite",
    })

    def _detect_prompt_type(self, user_message: str) -> str:
        """Detect whether user intent is resume generation or advisory chat."""
        msg_lower = user_message.lower()
        if any(kw in msg_lower for kw in self._RESUME_KEYWORDS):
            return "resume_generation"
        return "chat"

    def _build_messages(
        self, existing_messages: List[ChatMessage], new_user_message: str, db: Session = None
    ) -> List[Dict[str, str]]:
        """Build message array for AI provider with full conversation history.

        Uses Prompt Intelligence v2 for system prompt construction.
        Preserves exact message ordering: [system] + [history...] + [user].
        Injects knowledge rules from knowledge_intelligence when db is available.
        Detects resume-generation intent and uses appropriate prompt type.
        """
        # Build conversation history from DB messages
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in existing_messages
        ]

        # Always use "chat" prompt type for chat messages.
        # The chat system prompt instructs the AI to output structured JSON
        # (action: generate_resume) when it has enough resume information.
        # Using "resume_generation" here fails because _build_messages never
        # provides resume_knowledge in context, causing an empty user prompt.
        prompt_type = "chat"

        # Retrieve knowledge rules for chat context
        context = {
            "user_message": new_user_message,
            "conversation_history": history,
        }
        if db:
            try:
                from app.services.ai_service import get_knowledge_rules_for_context
                knowledge_rules = get_knowledge_rules_for_context(db)
                if knowledge_rules:
                    context["knowledge_rules"] = knowledge_rules
            except Exception as e:
                logger.warning("Failed to retrieve knowledge rules for chat: %s", e)

        # Use v2 builder for system prompt + user message
        request = PromptRequest(
            prompt_type=prompt_type,
            context=context,
        )
        messages = self._prompt_builder_v2.build_messages(request)

        # Insert conversation history between system and user
        # v2 produces [system, user]; we need [system, history..., user]
        if history:
            messages = [messages[0]] + history + [messages[1]]

        return messages

    def _validate_resume_output(
        self,
        structured_data: Dict[str, Any],
        user_message: str,
        db: Session = None,
    ) -> Optional[Dict[str, Any]]:
        """Validate AI-generated resume output using governed validators.

        Runs schema, truth, and knowledge validation directly against the
        parsed response data. Does not require an AIExecution DB record.
        Returns validation summary dict or None if validation cannot run.
        """
        try:
            from app.services.ai_service import validate_resume_output
            return validate_resume_output(structured_data, user_message, db=db)
        except Exception as e:
            logger.warning("Resume validation failed: %s", e)
            return None

    def _extract_structured_data(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract structured resume data from AI response if present."""
        try:
            if "```json" in content and "```" in content:
                start = content.index("```json") + 7
                end = content.index("```", start)
                json_str = content[start:end].strip()
                data = json.loads(json_str)
                if "action" in data and data["action"] == "generate_resume":
                    return data.get("data")
        except (json.JSONDecodeError, ValueError):
            pass
        return None

    def _generate_title(self, first_message: str) -> str:
        """Generate a session title from the first message."""
        title = first_message[:50].strip()
        if len(first_message) > 50:
            title += "..."
        return title

    def close_session(self, db: Session, session_id: str) -> bool:
        """Close a chat session."""
        session = self.get_session(db, session_id)
        if session:
            session.status = "closed"
            db.commit()
            return True
        return False

    def delete_session(self, db: Session, session_id: str) -> bool:
        """Delete a chat session and all its messages."""
        session = self.get_session(db, session_id)
        if session:
            db.delete(session)
            db.commit()
            return True
        return False
