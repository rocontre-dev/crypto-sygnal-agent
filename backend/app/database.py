"""Database connection and session management."""

import logging

from sqlalchemy import create_engine as sync_create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.pool import NullPool

from .core.config import settings

logger = logging.getLogger(__name__)

# Track if database is available
_db_available = False
engine = None
sync_engine = None

# Create async engine for database connections
try:
    engine = create_async_engine(
        settings.async_database_url,
        echo=settings.DEBUG,
        poolclass=NullPool,
        future=True,
    )
    _db_available = True
except Exception as e:
    logger.warning(
        f"Failed to create async database engine: {e}. "
        "Running without database connection. Mock data will be used."
    )
    _db_available = False

# Create sync engine for migrations (only if async engine is available)
if _db_available:
    try:
        sync_engine = sync_create_engine(
            settings.database_url,
            echo=settings.DEBUG,
            future=True,
        )
    except Exception as e:
        logger.warning(f"Failed to create sync database engine: {e}")

# Async session factory (only created if engine is available)
if engine is not None:
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
else:
    AsyncSessionLocal = None

# Sync session factory for migrations (only created if sync_engine is available)
if sync_engine is not None:
    SessionLocal = Session(
        bind=sync_engine,
        autoflush=False,
        autocommit=False,
    )
else:
    SessionLocal = None


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


async def get_db() -> AsyncSession:
    """Dependency that provides a database session.

    Yields:
        AsyncSession: Database session

    Raises:
        Exception: Re-raises any exception after ensuring session is closed
    """
    if AsyncSessionLocal is None:
        raise RuntimeError(
            "Database is not available. "
            "The application is running in offline mode with mock data."
        )
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables."""
    if engine is None:
        logger.warning("Skipping database initialization: database is not available.")
        return
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.warning(f"Failed to initialize database tables: {e}")


async def close_db() -> None:
    """Close database connections."""
    if engine is not None:
        await engine.dispose()
        logger.info("Database connections closed.")


def is_db_available() -> bool:
    """Check if database is available."""
    return _db_available