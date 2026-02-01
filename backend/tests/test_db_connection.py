"""
Quick test to verify database connection and task creation works.
Run with: cd backend && python -m tests.test_db_connection
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import db
from app.core.config import settings


async def test_db_connection():
    """Test database connection and basic queries."""
    print("Testing database connection...")

    try:
        # Test connection
        await db.connect()
        print("✅ Database connected successfully")

        # Test basic query
        result = await db.fetchval("SELECT 1")
        print(f"✅ Basic query successful: {result}")

        # Test task table exists
        tables = await db.fetch("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        table_names = [row['tablename'] for row in tables]
        print(f"📋 Tables in database: {table_names}")

        if 'task' in table_names:
            print("✅ Task table exists")

            # Check task table structure
            columns = await db.fetch("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'task'
                ORDER BY ordinal_position
            """)
            print("📋 Task table columns:")
            for col in columns:
                print(f"   - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        else:
            print("❌ Task table NOT found!")

        # Test creating a task
        print("\n🧪 Testing task creation...")
        import uuid
        from datetime import datetime

        task_id = str(uuid.uuid4())
        test_user_id = "test-user-123"

        # First, let's see if there's a user with this ID
        user = await db.fetchrow('SELECT * FROM "user" WHERE id = $1', test_user_id)
        if not user:
            print(f"⚠️ Test user not found, creating one...")
            # Create a test user
            await db.execute(
                """INSERT INTO "user" (id, name, email, "emailVerified")
                   VALUES ($1, $2, $3, $4)
                   ON CONFLICT (id) DO NOTHING""",
                test_user_id, "Test User", "test@example.com", True
            )
            print("✅ Test user created")

        # Now try to create a task
        result = await db.fetchrow(
            """
            INSERT INTO task (id, title, description, priority, status, tags, "userId", "createdAt", "updatedAt")
            VALUES ($1, $2, $3, $4, 'PENDING', $5, $6, NOW(), NOW())
            RETURNING id, title, description, priority, status
            """,
            task_id, "Test Task from DB Check", "This is a test task", "HIGH", [], test_user_id
        )

        if result:
            print(f"✅ Task created successfully: {result['title']}")
            print(f"   ID: {result['id']}")
            print(f"   Status: {result['status']}")
            print(f"   Priority: {result['priority']}")

            # Clean up test task
            await db.execute('DELETE FROM task WHERE id = $1', task_id)
            print("🧹 Test task cleaned up")
        else:
            print("❌ Failed to create task")

        await db.disconnect()
        print("\n✅ All tests passed!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        await db.disconnect()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_db_connection())
