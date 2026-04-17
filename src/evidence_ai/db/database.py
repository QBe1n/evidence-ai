"""SQLAlchemy async engine and session factory.

Sets up the async database connection pool and provides:
- ``engine``: The global async engine
- ``AsyncSessionLocal``: Session factory
- ``init_db()``: Create tables on startup
- ``close_db()``: Close connection pool on shutdown
"""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from evidence_ai.config import settings

logger = logging.getLogger(__name__)

# Create the async engine
engine = create_async_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,       # Reconnect if connection is stale
    pool_recycle=3600,        # Recycle connections after 1 hour
    echo=settings.app_env == "development",  # Log SQL in development
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


async def init_db() -> None:
    """Create database tables if they don't exist.

    Called during application startup. In production, use Alembic migrations
    instead of ``create_all()``.
    """
    from evidence_ai.db import models  # noqa: F401 — ensure models are registered

    async with engine.begin() as conn:
        if settings.app_env == "development":
            # In development, create tables automatically
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables initialized")
        else:
            # In production, Alembic migrations should have already run
            logger.info("Database initialized (production: relying on Alembic migrations)")


async def close_db() -> None:
    """Close all database connections gracefully."""
    await engine.dispose()
    logger.info("Database connection pool closed")
