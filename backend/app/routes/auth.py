"""
Authentication Routes
=====================

FastAPI routes for user authentication functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.db import get_db_session
from ..core.security import get_current_user, TokenPayload
from ..models.auth import UserRegistrationRequest, UserLoginRequest, UserResponse, TokenResponse, AuthStatusResponse
from ..models.task import TaskResponse


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserRegistrationRequest, db: AsyncSession = Depends(get_db_session)):
    """
    Register a new user.

    Args:
        user_data: User registration information
        db: Database session

    Returns:
        UserResponse: Created user information
    """
    # In a real implementation, this would create a user in the database
    # For now, we'll simulate the response
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User registration endpoint not fully implemented yet"
    )


@router.post("/login", response_model=TokenResponse)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and return access token.

    Args:
        form_data: OAuth2 form data with username/email and password

    Returns:
        TokenResponse: JWT access token
    """
    # In a real implementation, this would verify credentials against the database
    # For now, we'll simulate the response
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User login endpoint not fully implemented yet"
    )


@router.post("/logout")
async def logout_user(current_user: TokenPayload = Depends(get_current_user)):
    """
    Logout the current user.

    Args:
        current_user: Currently authenticated user (from JWT token)

    Returns:
        Success message
    """
    # In a real implementation, this might invalidate the token
    return {"message": f"User {current_user.sub} logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: TokenPayload = Depends(get_current_user)):
    """
    Get information about the currently authenticated user.

    Args:
        current_user: Currently authenticated user (from JWT token)

    Returns:
        UserResponse: Current user information
    """
    # In a real implementation, this would fetch user details from the database
    # For now, we'll simulate the response
    return UserResponse(
        id=current_user.sub,
        email=current_user.email or "",
        name=current_user.name or "",
        created_at=None  # Would be fetched from database in real implementation
    )


@router.get("/status", response_model=AuthStatusResponse)
async def get_auth_status(current_user: TokenPayload = Depends(get_current_user)):
    """
    Check authentication status of the current user.

    Args:
        current_user: Currently authenticated user (from JWT token)

    Returns:
        AuthStatusResponse: Authentication status and user information
    """
    user_info = await get_current_user_info(current_user)

    return AuthStatusResponse(
        authenticated=True,
        user=user_info,
        message="User is authenticated"
    )