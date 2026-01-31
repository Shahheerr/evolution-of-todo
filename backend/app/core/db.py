"""
Database Connection Module
==========================

This module handles database connections and session management
for the FastAPI backend application using asyncpg for PostgreSQL.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from .config import settings


# Create the async database engine
engine = create_async_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG,  # Enable SQL logging in debug mode
)

# Create async session maker
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to provide database sessions for FastAPI endpoints.

    Yields:
        AsyncSession: Database session for queries and transactions
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Utility functions for database operations
async def init_db() -> None:
    """
    Initialize the database (create tables if needed).
    This function can be called at application startup.
    """
    async with engine.begin() as conn:
        # Create all tables (this is a simplified version)
        # In a real application, you'd likely use Alembic for migrations
        pass


async def close_db() -> None:
    """
    Close the database engine connection pool.
    This function should be called at application shutdown.
    """
    await engine.dispose()