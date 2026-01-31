"""
FastAPI Todo Application - Main Entry Point.

This is the main application that brings everything together:
- Database connection management (lifespan)
- CORS configuration (for frontend communication)
- Route registration
- Health check endpoints
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import db
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
    ## Todo API - Production-Grade Task Management
    
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
    
    ### Authentication
    All endpoints require a valid JWT token in the Authorization header:
    ```
    Authorization: Bearer <your-jwt-token>
    ```
    """,
    version="1.0.0",
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
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
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
        "app": settings.APP_NAME
    }


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
