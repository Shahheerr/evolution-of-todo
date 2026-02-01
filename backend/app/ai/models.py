"""
AI Chat Models

Pydantic models for AI chat request/response and SSE streaming.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request body for POST /api/chat"""
    message: str = Field(..., min_length=1, max_length=1000, description="User's message to the AI")
    session_id: Optional[str] = Field(None, description="Existing session ID to resume conversation")


class ChatStreamChunk(BaseModel):
    """Single event in the SSE stream"""
    type: Literal["content", "tool_call", "error", "done"]
    content: Optional[str] = None
    tool_call: Optional[dict] = None
    error: Optional[str] = None
    session_id: Optional[str] = None  # Included in first chunk


class ToolCallData(BaseModel):
    """Tool call data for SSE events"""
    id: str
    name: str
    arguments: dict


class ToolCallEvent(BaseModel):
    """Tool call event for streaming"""
    type: Literal["tool_call"]
    tool_call: ToolCallData


class ContentEvent(BaseModel):
    """Content event for streaming"""
    type: Literal["content"]
    content: str
    session_id: Optional[str] = None


class ErrorEvent(BaseModel):
    """Error event for streaming"""
    type: Literal["error"]
    error: str


class DoneEvent(BaseModel):
    """Done event for streaming"""
    type: Literal["done"]
