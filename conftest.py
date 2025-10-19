import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import get_db
from app.models import tax_lot, price
from decimal import Decimal
from datetime import datetime, timedelta
import os

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_position_tracker.db"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(tax_lot.Base.metadata.create_all)
        await conn.run_sync(price.Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(tax_lot.Base.metadata.drop_all)
        await conn.run_sync(price.Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def test_db(test_engine):
    """Create test database session."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
def client(test_db):
    """Create test client with database dependency override."""
    app.dependency_overrides[get_db] = lambda: test_db
    
    from fastapi.testclient import TestClient
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
async def sample_user_id():
    """Sample user ID for testing."""
    return 123

@pytest.fixture
async def sample_security_id():
    """Sample security ID for testing."""
    return 1

@pytest.fixture
async def sample_trades_data():
    """Sample trade data for testing."""
    return [
        {
            "user_id": 123,
            "security_id": 1,
            "side": "BUY",
            "quantity": 100.0,
            "price": 150.0,
            "timestamp": "2024-01-01T10:00:00Z",
            "charges": 5.0
        },
        {
            "user_id": 123,
            "security_id": 1,
            "side": "BUY",
            "quantity": 50.0,
            "price": 160.0,
            "timestamp": "2024-01-15T10:00:00Z",
            "charges": 3.0
        },
        {
            "user_id": 123,
            "security_id": 1,
            "side": "SELL",
            "quantity": 75.0,
            "price": 170.0,
            "timestamp": "2024-02-01T10:00:00Z",
            "charges": 4.0
        }
    ]

@pytest.fixture
async def cleanup_test_db():
    """Cleanup function to remove test database file."""
    yield
    if os.path.exists("test_position_tracker.db"):
        os.remove("test_position_tracker.db")
