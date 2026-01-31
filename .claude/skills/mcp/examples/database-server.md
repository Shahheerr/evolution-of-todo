# MCP Database Server Example

Complete example of an MCP server that provides database access tools.

## Dependencies

```bash
pip install mcp asyncpg
```

## Server Implementation

```python
"""
MCP Database Server

Provides tools for querying a PostgreSQL database.
"""

from typing import Optional, List, Any
import asyncpg
from mcp.server.fastmcp import FastMCP, Context
from mcp.types import McpError, ErrorCode

# Create server
mcp = FastMCP(
    name="database-server",
    version="1.0.0",
    description="MCP server for database operations"
)

# Database connection pool
pool: Optional[asyncpg.Pool] = None

# Configuration
DATABASE_URL = "postgresql://user:pass@localhost/dbname"
ALLOWED_TABLES = ["users", "products", "orders", "categories"]

# =============================================================================
# Lifecycle
# =============================================================================

@mcp.on_startup
async def startup():
    """Initialize database connection pool."""
    global pool
    pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=2,
        max_size=10
    )
    print("Database connected")

@mcp.on_shutdown
async def shutdown():
    """Close database connection pool."""
    global pool
    if pool:
        await pool.close()
        print("Database disconnected")

# =============================================================================
# Helper Functions
# =============================================================================

def validate_table(table: str) -> None:
    """Validate table name to prevent SQL injection."""
    if table not in ALLOWED_TABLES:
        raise McpError(
            ErrorCode.InvalidParams,
            f"Invalid table '{table}'. Allowed: {ALLOWED_TABLES}"
        )

def format_rows(rows: List[asyncpg.Record], table: str) -> str:
    """Format database rows as readable string."""
    if not rows:
        return f"No data found in {table}"
    
    result = f"Results from {table} ({len(rows)} rows):\n\n"
    
    for i, row in enumerate(rows, 1):
        result += f"[{i}]\n"
        for key, value in dict(row).items():
            result += f"  {key}: {value}\n"
        result += "\n"
    
    return result

# =============================================================================
# Tools
# =============================================================================

@mcp.tool()
async def list_tables(ctx: Context) -> str:
    """
    List all available database tables.
    """
    await ctx.info("Listing available tables...")
    return f"Available tables:\n" + "\n".join(f"  - {t}" for t in ALLOWED_TABLES)

@mcp.tool()
async def describe_table(ctx: Context, table: str) -> str:
    """
    Get the schema of a table.
    
    Args:
        table: Name of the table to describe
    """
    validate_table(table)
    
    await ctx.info(f"Describing table: {table}")
    
    async with pool.acquire() as conn:
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = $1
            ORDER BY ordinal_position
        """, table)
    
    if not columns:
        return f"Table '{table}' has no columns or doesn't exist"
    
    result = f"Schema for {table}:\n\n"
    for col in columns:
        nullable = "NULL" if col["is_nullable"] == "YES" else "NOT NULL"
        default = f" DEFAULT {col['column_default']}" if col["column_default"] else ""
        result += f"  {col['column_name']}: {col['data_type']} {nullable}{default}\n"
    
    return result

@mcp.tool()
async def query_table(
    ctx: Context,
    table: str,
    columns: Optional[str] = None,
    where: Optional[str] = None,
    order_by: Optional[str] = None,
    limit: int = 20
) -> str:
    """
    Query data from a table.
    
    Args:
        table: Table name to query
        columns: Comma-separated column names (default: all)
        where: Simple WHERE condition (e.g., "status = 'active'")
        order_by: Column to sort by
        limit: Maximum rows to return (default: 20, max: 100)
    """
    validate_table(table)
    
    # Validate and constrain limit
    limit = min(max(1, limit), 100)
    
    # Build query
    select_cols = columns if columns else "*"
    query = f"SELECT {select_cols} FROM {table}"
    
    params = []
    if where:
        # Note: In production, use parameterized queries for WHERE
        # This is simplified for the example
        query += f" WHERE {where}"
    
    if order_by:
        query += f" ORDER BY {order_by}"
    
    query += f" LIMIT {limit}"
    
    await ctx.info(f"Executing query on {table}...")
    await ctx.debug(f"Query: {query}")
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
    
    return format_rows(rows, table)

@mcp.tool()
async def count_rows(
    ctx: Context,
    table: str,
    where: Optional[str] = None
) -> str:
    """
    Count rows in a table.
    
    Args:
        table: Table name
        where: Optional WHERE condition
    """
    validate_table(table)
    
    query = f"SELECT COUNT(*) as count FROM {table}"
    if where:
        query += f" WHERE {where}"
    
    async with pool.acquire() as conn:
        result = await conn.fetchrow(query)
    
    count = result["count"]
    condition = f" where {where}" if where else ""
    return f"Count of {table}{condition}: {count}"

@mcp.tool()
async def aggregate(
    ctx: Context,
    table: str,
    operation: str,
    column: str,
    group_by: Optional[str] = None
) -> str:
    """
    Perform aggregation on a table.
    
    Args:
        table: Table name
        operation: Aggregation operation (count, sum, avg, min, max)
        column: Column to aggregate
        group_by: Optional column to group by
    """
    validate_table(table)
    
    valid_ops = ["count", "sum", "avg", "min", "max"]
    if operation.lower() not in valid_ops:
        raise McpError(
            ErrorCode.InvalidParams,
            f"Invalid operation. Use: {valid_ops}"
        )
    
    agg = f"{operation.upper()}({column})"
    
    if group_by:
        query = f"SELECT {group_by}, {agg} as result FROM {table} GROUP BY {group_by} ORDER BY result DESC LIMIT 20"
    else:
        query = f"SELECT {agg} as result FROM {table}"
    
    await ctx.info(f"Calculating {operation}({column}) on {table}")
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
    
    if group_by:
        result = f"{operation.upper()}({column}) by {group_by}:\n\n"
        for row in rows:
            result += f"  {row[group_by]}: {row['result']}\n"
        return result
    else:
        return f"{operation.upper()}({column}) = {rows[0]['result']}"

# =============================================================================
# Resources
# =============================================================================

@mcp.resource("db://schema")
async def get_full_schema() -> str:
    """Get schema for all tables."""
    result = "Database Schema\n" + "=" * 40 + "\n\n"
    
    for table in ALLOWED_TABLES:
        async with pool.acquire() as conn:
            columns = await conn.fetch("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = $1
                ORDER BY ordinal_position
            """, table)
        
        result += f"Table: {table}\n"
        for col in columns:
            result += f"  - {col['column_name']}: {col['data_type']}\n"
        result += "\n"
    
    return result

@mcp.resource("db://stats")
async def get_table_stats() -> str:
    """Get row counts for all tables."""
    result = "Table Statistics\n" + "=" * 40 + "\n\n"
    
    for table in ALLOWED_TABLES:
        async with pool.acquire() as conn:
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
        result += f"  {table}: {count} rows\n"
    
    return result

# =============================================================================
# Run Server
# =============================================================================

if __name__ == "__main__":
    mcp.run()
```

## Usage

### With Claude Desktop

```json
{
  "mcpServers": {
    "database": {
      "command": "python",
      "args": ["/path/to/database_server.py"],
      "env": {
        "DATABASE_URL": "postgresql://user:pass@localhost/dbname"
      }
    }
  }
}
```

### With MCP Client

```python
from mcp import ClientSession
from mcp.client.stdio import stdio_client

async def main():
    async with stdio_client(
        command="python",
        args=["database_server.py"]
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List tables
            result = await session.call_tool("list_tables", {})
            print(result.content[0].text)
            
            # Query data
            result = await session.call_tool("query_table", {
                "table": "users",
                "limit": 5
            })
            print(result.content[0].text)
```
