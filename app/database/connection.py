from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Check if using SQLite or PostgreSQL
is_sqlite = "sqlite" in settings.DATABASE_URL.lower()

if is_sqlite:
    engine = create_async_engine(
        settings.DATABASE_URL,
        # Required for SQLite only
        connect_args={"check_same_thread": False}
    )
else:
    # Convert PostgreSQL URL to use asyncpg for async operations
    async_database_url = settings.DATABASE_URL.replace('postgresql+psycopg2://', 'postgresql+asyncpg://')
    
    # PostgreSQL configuration
    engine = create_async_engine(
        async_database_url,
        echo=False,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)