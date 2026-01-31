"""
Main Application Entry Point
============================

FastAPI application with JWT authentication using Better-Auth secret.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.security import get_current_user, TokenPayload

# Create FastAPI app instance
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Allow Authorization header for JWT
    allow_credentials=True,
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Backend API is running", "app": settings.APP_NAME}


@app.get("/protected")
async def protected_endpoint(current_user: TokenPayload = Depends(get_current_user)):
    """Example protected endpoint that requires authentication."""
    return {
        "message": "This is a protected endpoint",
        "user_id": current_user.sub,
        "email": current_user.email,
        "authenticated": True
    }


# Include routes (will be added as we develop more features)
# from .routes import tasks
# app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )