"""
Database module - PostgreSQL connection using asyncpg.

This module handles the database connection to Neon PostgreSQL.
We use raw SQL queries via asyncpg for simplicity on the Python backend.
Prisma is used on the frontend for schema management and migrations.
"""

import asyncpg
from contextlib import asynccontextmanager
from typing import Optional, AsyncGenerator

from app.core.config import settings


# =============================================================================
# Database Connection Pool
# =============================================================================

class Database:
    """
    Database connection manager using asyncpg connection pool.
    """
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self) -> None:
        """
        Initialize the connection pool.
        Call this on application startup.
        """
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                settings.DATABASE_URL,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
    
    async def disconnect(self) -> None:
        """
        Close the connection pool.
        Call this on application shutdown.
        """
        if self.pool:
            await self.pool.close()
            self.pool = None
    
    async def execute(self, query: str, *args) -> str:
        """
        Execute a query that doesn't return results (INSERT, UPDATE, DELETE).
        """
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)
    
    async def fetch(self, query: str, *args) -> list:
        """
        Execute a query and fetch all results.
        """
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """
        Execute a query and fetch a single row.
        """
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args):
        """
        Execute a query and fetch a single value.
        """
        async with self.pool.acquire() as connection:
            return await connection.fetchval(query, *args)


# Global database instance
db = Database()


# =============================================================================
# Dependency for FastAPI
# =============================================================================

async def get_db() -> Database:
    """
    FastAPI dependency to get database instance.
    """
    return db


# =============================================================================
# Lifespan Context Manager
# =============================================================================

@asynccontextmanager
async def lifespan_db() -> AsyncGenerator[None, None]:
    """
    Context manager for database lifecycle.
    Use this with FastAPI lifespan.
    """
    await db.connect()
    try:
        yield
    finally:
        await db.disconnect()
