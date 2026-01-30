"""
Redis connection for sessions, presence, caching, and pub/sub.

Handles real-time features and ephemeral data.
"""
from typing import Optional
import redis.asyncio as aioredis

from app.core.config import settings


# Global Redis client
_redis: Optional[aioredis.Redis] = None


async def init_redis() -> None:
    """Initialize Redis connection."""
    global _redis
    
    _redis = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
    
    # Test connection
    await _redis.ping()
    print("✅ Redis connection initialized")


async def close_redis() -> None:
    """Close Redis connection."""
    global _redis
    if _redis:
        await _redis.close()
        print("🔌 Redis connection closed")


def get_redis() -> aioredis.Redis:
    """Get the Redis client."""
    if not _redis:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return _redis


# ===== User Presence =====

async def set_user_online(user_id: str) -> None:
    """Mark a user as online."""
    redis = get_redis()
    await redis.set(f"presence:{user_id}", "online", ex=60)  # Expires in 60s


async def set_user_offline(user_id: str) -> None:
    """Mark a user as offline."""
    redis = get_redis()
    await redis.delete(f"presence:{user_id}")


async def is_user_online(user_id: str) -> bool:
    """Check if a user is online."""
    redis = get_redis()
    return await redis.exists(f"presence:{user_id}") > 0


async def refresh_presence(user_id: str) -> None:
    """Refresh user presence (called on activity)."""
    redis = get_redis()
    await redis.expire(f"presence:{user_id}", 60)


# ===== Match Queue =====

async def add_to_match_queue(user_id: str, score: float) -> None:
    """Add user to the matching queue with a priority score."""
    redis = get_redis()
    await redis.zadd("match_queue", {user_id: score})


async def remove_from_match_queue(user_id: str) -> None:
    """Remove user from the matching queue."""
    redis = get_redis()
    await redis.zrem("match_queue", user_id)


async def get_match_queue(limit: int = 100) -> list:
    """Get users in the match queue ordered by score."""
    redis = get_redis()
    return await redis.zrevrange("match_queue", 0, limit - 1, withscores=True)


# ===== Session Management =====

async def store_session(session_id: str, data: dict, expire_seconds: int = 3600) -> None:
    """Store session data."""
    redis = get_redis()
    await redis.hset(f"session:{session_id}", mapping=data)
    await redis.expire(f"session:{session_id}", expire_seconds)


async def get_session(session_id: str) -> Optional[dict]:
    """Get session data."""
    redis = get_redis()
    data = await redis.hgetall(f"session:{session_id}")
    return data if data else None


async def delete_session(session_id: str) -> None:
    """Delete a session."""
    redis = get_redis()
    await redis.delete(f"session:{session_id}")


# ===== Pub/Sub for Real-time Events =====

async def publish_event(channel: str, message: str) -> None:
    """Publish an event to a channel."""
    redis = get_redis()
    await redis.publish(channel, message)


async def get_pubsub():
    """Get a pub/sub connection for subscribing to events."""
    redis = get_redis()
    return redis.pubsub()
