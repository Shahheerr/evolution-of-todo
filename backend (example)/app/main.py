"""
FastAPI Todo Application - Main Entry Point.

This is the main application that brings everything together:
- Database connection management (lifespan)
- CORS configuration (for frontend communication)
- Route registration
- Health check endpoints
- AI-powered chat integration
"""

import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse
from pydantic import BaseModel

from app.core.config import settings
from app.core.database import db
from app.core.security import verify_jwt_token
from app.routes import tasks


# =============================================================================
# Application Lifespan (Startup/Shutdown)
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.
    - Startup: Connect to database
    - Shutdown: Disconnect from database
    """
    # Startup
    print(">> Starting Todo API...")
    await db.connect()
    print(">> Database connected successfully")
    print(f">> AI Features: {'Enabled' if settings.OPENAI_API_KEY else 'Disabled (no API key)'}")
    
    yield
    
    # Shutdown
    print(">> Shutting down Todo API...")
    await db.disconnect()
    print(">> Database disconnected")


# =============================================================================
# Application Instance
# =============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## Todo API - Production-Grade Task Management with AI
    
    This API provides full CRUD operations for managing tasks with:
    - 🔐 **JWT Authentication** (via Better Auth tokens)
    - 📝 **Full CRUD** (Create, Read, Update, Delete)
    - ✅ **Status Management** (Complete/Incomplete)
    - 🏷️ **Priority Levels** (High/Medium/Low)
    - 🔖 **Tags** for organization
    - 🔍 **Search** by keyword
    - 🎯 **Filter** by status/priority/tag
    - 📊 **Sort** by date/priority
    - 📄 **Pagination** support
    - 🤖 **AI Chat** (via OpenAI function calling)
    
    ### Authentication
    All endpoints require a valid JWT token in the Authorization header:
    ```
    Authorization: Bearer <your-jwt-token>
    ```
    
    ### AI Chat
    Use the `/api/chat` endpoint to interact with the AI assistant.
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# =============================================================================
# CORS Middleware
# =============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


# =============================================================================
# Health Check Endpoints
# =============================================================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API welcome message."""
    return {
        "message": "Welcome to Todo API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "ai_enabled": bool(settings.OPENAI_API_KEY)
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Test database connection
        await db.fetchval("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "app": settings.APP_NAME,
        "ai_enabled": bool(settings.OPENAI_API_KEY)
    }


# =============================================================================
# AI Chat Endpoint
# =============================================================================

class ChatRequest(BaseModel):
    """Request body for AI chat."""
    message: str


class ChatResponse(BaseModel):
    """Response from AI chat."""
    response: str
    success: bool = True


@app.post("/api/chat", tags=["AI"], response_model=ChatResponse)
async def ai_chat_endpoint(request: Request, body: ChatRequest) -> ChatResponse:
    """
    AI Chat endpoint for conversational task management.
    
    This endpoint:
    1. Authenticates the user via JWT token
    2. Passes the message to the AI agent
    3. The AI uses function calling to manage tasks
    4. Returns the AI response
    
    Requires Authorization header with Bearer token.
    """
    try:
        from app.ai.agent import chat_with_ai
        
        # Get the authorization header
        auth_header = request.headers.get("Authorization", "")
        user_id = "anonymous"
        
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                # Verify JWT and extract user ID
                token_payload = verify_jwt_token(token)
                user_id = token_payload.sub
                print(f"🔐 AI Chat: Authenticated user {user_id}")
            except Exception as e:
                print(f"⚠️ AI Chat: JWT verification failed: {e}")
                return ChatResponse(
                    response="❌ Authentication failed. Please log in again.",
                    success=False
                )
        else:
            return ChatResponse(
                response="❌ Not authenticated. Please log in to use AI features.",
                success=False
            )
        
        # Get AI response
        response = await chat_with_ai(user_id=user_id, message=body.message)
        
        return ChatResponse(response=response, success=True)
        
    except ImportError as e:
        print(f"❌ AI Import Error: {e}")
        return ChatResponse(
            response="⚠️ AI features not available. Please check server configuration.",
            success=False
        )
    except Exception as e:
        print(f"❌ AI Chat Error: {e}")
        traceback.print_exc()
        return ChatResponse(
            response=f"❌ An error occurred: {str(e)}",
            success=False
        )


# =============================================================================
# Register Routes
# =============================================================================

app.include_router(tasks.router, prefix="/api")


# =============================================================================
# Run with Uvicorn (for development)
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
