"""
AI Chatbot Module

This module provides AI-powered task management through natural language.
It uses OpenAI's function calling API to execute task operations.
"""

from app.ai.models import ChatRequest, ChatStreamChunk

__all__ = ["ChatRequest", "ChatStreamChunk"]
