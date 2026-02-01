"""
Session Management for AI Chat

In-memory storage for conversation history and session state.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any


class ChatSession:
    """
    Represents a conversation session between a user and the AI assistant.

    Sessions are stored in-memory (no database persistence) and expire after 24 hours.
    """

    def __init__(self, user_id: str):
        self.session_id: str = str(uuid.uuid4())
        self.user_id: str = user_id
        self.messages: List[Dict[str, Any]] = []
        self.created_at: datetime = datetime.utcnow()
        self.last_activity: datetime = datetime.utcnow()

    def add_message(self, role: str, content: str | None, tool_calls: List | None = None) -> None:
        """
        Add a message to the conversation history.

        Args:
            role: Message role ("system", "user", "assistant", "tool")
            content: Message text content
            tool_calls: Optional tool calls from assistant
        """
        msg: Dict[str, Any] = {"role": role, "content": content}
        if tool_calls:
            msg["tool_calls"] = tool_calls
        self.messages.append(msg)
        self.last_activity = datetime.utcnow()

        # Enforce 10-message limit (keep system prompt + last 10 exchanges)
        if len(self.messages) > 21:  # 1 system + 10 user + 10 assistant
            self.messages = [self.messages[0]] + self.messages[-20:]

    def get_messages_for_api(self) -> List[Dict[str, Any]]:
        """Get messages formatted for OpenAI API."""
        return self.messages.copy()

    def is_expired(self, timeout_hours: int = 24) -> bool:
        """Check if session has expired due to inactivity."""
        expiry_time = self.last_activity + timedelta(hours=timeout_hours)
        return datetime.utcnow() > expiry_time


# Global session storage (production could use Redis)
_sessions: Dict[str, ChatSession] = {}


def get_or_create_session(user_id: str, session_id: Optional[str] = None) -> ChatSession:
    """
    Get an existing session or create a new one.

    Args:
        user_id: The authenticated user's ID
        session_id: Optional existing session ID to resume

    Returns:
        ChatSession instance
    """
    # Clean up expired sessions periodically (simple cleanup on access)
    _cleanup_expired_sessions()

    if session_id:
        session = _sessions.get(session_id)
        if session and session.user_id == user_id and not session.is_expired():
            return session

    # Create new session
    session = ChatSession(user_id)
    _sessions[session.session_id] = session
    return session


def _cleanup_expired_sessions() -> None:
    """Remove expired sessions from memory."""
    global _sessions
    now = datetime.utcnow()
    _sessions = {
        sid: s for sid, s in _sessions.items()
        if not s.is_expired()
    }


def get_session(session_id: str) -> Optional[ChatSession]:
    """Get a session by ID."""
    return _sessions.get(session_id)


def delete_session(session_id: str) -> bool:
    """Delete a session by ID."""
    if session_id in _sessions:
        del _sessions[session_id]
        return True
    return False
