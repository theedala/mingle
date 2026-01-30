"""
Mingle Backend - Privacy-First Social Matching Platform

FastAPI application with WebSocket support for real-time chat.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.postgres import init_postgres, close_postgres
from app.db.redis import init_redis, close_redis
from app.db.mongodb import init_mongodb, close_mongodb
from app.db.clickhouse import init_clickhouse, close_clickhouse
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown."""
    # Startup: Initialize all database connections
    await init_postgres()
    await init_redis()
    await init_mongodb()
    await init_clickhouse()
    
    yield
    
    # Shutdown: Close all database connections
    await close_postgres()
    await close_redis()
    await close_mongodb()
    await close_clickhouse()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Mingle API",
        description="Privacy-first social matching platform with real-time chat",
        version="1.0.0",
        lifespan=lifespan,
    )
    
    # Configure CORS - allow frontend access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    return app


app = create_app()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "mingle-api"}
