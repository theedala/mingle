"""
MongoDB connection using Motor (async driver).

Handles chat messages with flexible schema and TTL for ephemeral messages.
"""
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings


# Global MongoDB client and database
_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


async def init_mongodb() -> None:
    """Initialize MongoDB connection."""
    global _client, _db
    
    _client = AsyncIOMotorClient(settings.MONGODB_URL)
    _db = _client[settings.MONGODB_DB]
    
    # Create indexes for chat messages
    await _db.messages.create_index([("conversation_id", 1), ("timestamp", 1)])
    await _db.messages.create_index([("expires_at", 1)], expireAfterSeconds=0)  # TTL index
    
    # Create indexes for conversations
    await _db.conversations.create_index([("participants", 1)])
    await _db.conversations.create_index([("created_at", -1)])
    
    print("✅ MongoDB connection initialized")


async def close_mongodb() -> None:
    """Close MongoDB connection."""
    global _client
    if _client:
        _client.close()
        print("🔌 MongoDB connection closed")


def get_mongodb() -> AsyncIOMotorDatabase:
    """Get the MongoDB database."""
    if not _db:
        raise RuntimeError("MongoDB not initialized. Call init_mongodb() first.")
    return _db


# ===== Chat Collections =====

def get_messages_collection():
    """Get the messages collection."""
    return get_mongodb().messages


def get_conversations_collection():
    """Get the conversations collection."""
    return get_mongodb().conversations


def get_reactions_collection():
    """Get the reactions collection."""
    return get_mongodb().reactions
