"""
Chat Routes

AI chat endpoint with SSE streaming for task management.
"""

import logging
from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.security import AuthenticatedUser
from app.ai.agent import process_chat_stream

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    """Request body for POST /api/chat"""
    message: str
    session_id: str | None = None


@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    current_user: AuthenticatedUser
):
    """
    AI Chat endpoint with SSE streaming.

    - Accepts user message
    - Streams AI response as SSE events
    - Automatically handles tool execution
    - Maintains conversation context via session_id

    Authentication: Required (JWT Bearer token)
    """
    logger.info(f"Chat request from user {current_user.id}: {request.message[:50]}...")

    return StreamingResponse(
        process_chat_stream(
            message=request.message,
            user_id=current_user.id,  # Inject user_id from JWT for data isolation
            session_id=request.session_id
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
