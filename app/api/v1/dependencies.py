from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# Placeholder for auth dependency
async def get_current_user():
    # In a real app, this would validate a JWT and return the user model
    # For now, we'll return a dummy user ID.
    return {"id": 1, "username": "testuser"}