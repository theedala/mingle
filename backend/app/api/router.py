"""
Main API router - aggregates all route modules.
"""
from fastapi import APIRouter

from app.api.routes import profiles, matching, moderation, chat, analytics, video, icebreakers

api_router = APIRouter()

# Include route modules
api_router.include_router(
    profiles.router,
    prefix="/profiles",
    tags=["profiles"]
)

api_router.include_router(
    matching.router,
    prefix="/matching",
    tags=["matching"]
)

api_router.include_router(
    moderation.router,
    prefix="/moderation",
    tags=["moderation"]
)

api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["chat"]
)

api_router.include_router(
    video.router,
    prefix="/video",
    tags=["video"]
)

api_router.include_router(
    icebreakers.router,
    prefix="/icebreakers",
    tags=["icebreakers"]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["analytics"]
)
