#!/usr/bin/env python3
"""Test script to check if the roles table schema is created correctly"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.infrastructure.database.base import Base
from app.infrastructure.database.models import *  # Import all models


async def check_schema():
    # Create an in-memory SQLite database for testing
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Reflect the schema to check if the permissions column exists
    from sqlalchemy import text

    async with engine.begin() as conn:
        # Check columns in the roles table
        result = await conn.execute(text("PRAGMA table_info(roles);"))
        columns = result.fetchall()

        print("Columns in roles table:")
        for col in columns:
            print(f"  {col}")

        # Check if 'permissions' column exists
        permission_cols = [col for col in columns if col[1] == 'permissions']
        if permission_cols:
            print("\n✓ Permissions column exists!")
            print(f"Column details: {permission_cols[0]}")
        else:
            print("\n✗ Permissions column does NOT exist!")

        # Also check user_roles table
        result = await conn.execute(text("PRAGMA table_info(user_roles);"))
        user_roles_columns = result.fetchall()
        print(f"\nColumns in user_roles table:")
        for col in user_roles_columns:
            print(f"  {col}")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_schema())
