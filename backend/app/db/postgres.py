"""
PostgreSQL database connection using SQLAlchemy async.

Handles user profiles, preferences, reputation scores.
"""
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# Global engine and session factory
_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


async def init_postgres() -> None:
    """Initialize PostgreSQL connection pool."""
    global _engine, _session_factory
    
    _engine = create_async_engine(
        settings.POSTGRES_URL,
        echo=settings.DEBUG,
        pool_size=20,
        max_overflow=10,
        pool_pre_ping=True,
    )
    
    _session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    
    print("✅ PostgreSQL connection initialized")


async def close_postgres() -> None:
    """Close PostgreSQL connection pool."""
    global _engine
    if _engine:
        await _engine.dispose()
        print("🔌 PostgreSQL connection closed")


async def get_postgres_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session."""
    if not _session_factory:
        raise RuntimeError("PostgreSQL not initialized. Call init_postgres() first.")
    
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_engine() -> AsyncEngine:
    """Get the SQLAlchemy async engine."""
    if not _engine:
        raise RuntimeError("PostgreSQL not initialized. Call init_postgres() first.")
    return _engine
