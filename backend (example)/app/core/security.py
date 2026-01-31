"""
Security module - JWT Token Verification.

This module provides the core authentication mechanism for the FastAPI backend.
It verifies JWT tokens issued by Better Auth on the frontend and extracts user information.

THE CRITICAL FLOW:
1. Frontend (Next.js) authenticates user via Better Auth
2. Better Auth generates a JWT signed with BETTER_AUTH_SECRET
3. Frontend sends JWT in Authorization header: "Bearer <token>"
4. This module verifies the JWT signature using the SAME secret
5. Extracts user_id from the token payload
6. All database queries are filtered by this user_id (Data Isolation)
"""

from typing import Annotated, Optional
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from pydantic import BaseModel

from app.core.config import settings


# =============================================================================
# OAuth2 Bearer Token Scheme
# =============================================================================

# This tells FastAPI to look for the token in the Authorization header
# Format: "Authorization: Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",  # This is for OpenAPI docs, not actually used
    auto_error=True    # Automatically raise 401 if token is missing
)


# =============================================================================
# Token Payload Model
# =============================================================================

class TokenPayload(BaseModel):
    """
    Represents the decoded JWT token payload from Better Auth.
    Better Auth JWT tokens contain these standard claims.
    """
    sub: str              # Subject - the user ID
    email: Optional[str] = None
    name: Optional[str] = None
    iat: Optional[int] = None   # Issued At timestamp
    exp: Optional[int] = None   # Expiration timestamp


class CurrentUser(BaseModel):
    """
    Represents the authenticated user extracted from the JWT.
    This is what gets injected into route handlers.
    """
    id: str
    email: Optional[str] = None
    name: Optional[str] = None


# =============================================================================
# JWT Verification Functions
# =============================================================================

def verify_jwt_token(token: str) -> TokenPayload:
    """
    Verifies a JWT token and returns the decoded payload.
    
    Args:
        token: The JWT token string (without "Bearer " prefix)
    
    Returns:
        TokenPayload: The decoded and validated token payload
    
    Raises:
        HTTPException: If token is invalid, expired, or malformed
    """
    try:
        # Decode and verify the JWT using the shared secret
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={
                "verify_exp": True,      # Verify expiration
                "verify_iat": True,      # Verify issued at
                "require": ["sub", "exp"]  # Required claims
            }
        )
        
        # Validate the payload structure
        token_data = TokenPayload(**payload)
        
        # Additional validation: ensure user ID exists
        if not token_data.sub:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user identifier",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return token_data
        
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


# =============================================================================
# FastAPI Dependency - The Core Authentication Mechanism
# =============================================================================

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> CurrentUser:
    """
    FastAPI dependency that extracts and validates the current user from JWT.
    
    This is the PRIMARY authentication dependency. Use it in your routes:
    
    ```python
    @app.get("/tasks")
    async def get_tasks(current_user: CurrentUser = Depends(get_current_user)):
        # current_user.id is guaranteed to be valid here
        # Use it to filter all database queries
        tasks = await db.task.find_many(where={"userId": current_user.id})
        return tasks
    ```
    
    Args:
        token: JWT token from Authorization header (injected by FastAPI)
    
    Returns:
        CurrentUser: The authenticated user with id, email, and name
    
    Raises:
        HTTPException 401: If authentication fails
    """
    token_payload = verify_jwt_token(token)
    
    return CurrentUser(
        id=token_payload.sub,
        email=token_payload.email,
        name=token_payload.name
    )


# =============================================================================
# Type Alias for Clean Dependency Injection
# =============================================================================

# Use this type alias in your route handlers for cleaner code
AuthenticatedUser = Annotated[CurrentUser, Depends(get_current_user)]


# Example usage in routes:
# 
# from app.core.security import AuthenticatedUser
# 
# @router.get("/tasks")
# async def list_tasks(user: AuthenticatedUser):
#     # user.id contains the authenticated user's ID
#     # All queries MUST filter by user.id for data isolation
#     pass
