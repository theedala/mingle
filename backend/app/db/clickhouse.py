"""
ClickHouse connection for analytics and ML data pipeline.

Stores anonymized events for training matching models.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import clickhouse_connect

from app.core.config import settings


# Global ClickHouse client
_client = None


async def init_clickhouse() -> None:
    """Initialize ClickHouse connection and create tables."""
    global _client
    
    _client = clickhouse_connect.get_client(
        host=settings.CLICKHOUSE_HOST,
        port=settings.CLICKHOUSE_HTTP_PORT,
        username=settings.CLICKHOUSE_USER,
        password=settings.CLICKHOUSE_PASSWORD,
        database=settings.CLICKHOUSE_DB,
    )
    
    # Create analytics tables
    _client.command("""
        CREATE TABLE IF NOT EXISTS match_events (
            event_id UUID DEFAULT generateUUIDv4(),
            event_type String,
            user_hash String,
            partner_hash String,
            compatibility_score Float32,
            interests_matched Array(String),
            conversation_duration_seconds UInt32,
            messages_exchanged UInt32,
            quality_rating Nullable(UInt8),
            connection_type Enum8('text' = 1, 'video' = 2),
            outcome Enum8('completed' = 1, 'skipped' = 2, 'reported' = 3, 'disconnected' = 4),
            timestamp DateTime DEFAULT now()
        ) ENGINE = MergeTree()
        ORDER BY (timestamp, user_hash)
        TTL timestamp + INTERVAL 365 DAY
    """)
    
    _client.command("""
        CREATE TABLE IF NOT EXISTS user_activity (
            user_hash String,
            activity_type String,
            interests Array(String),
            vibe String,
            energy_level UInt8,
            session_duration_seconds UInt32,
            matches_accepted UInt32,
            matches_rejected UInt32,
            average_rating Float32,
            timestamp DateTime DEFAULT now()
        ) ENGINE = MergeTree()
        ORDER BY (timestamp, user_hash)
        TTL timestamp + INTERVAL 365 DAY
    """)
    
    print("✅ ClickHouse connection initialized")


async def close_clickhouse() -> None:
    """Close ClickHouse connection."""
    global _client
    if _client:
        _client.close()
        print("🔌 ClickHouse connection closed")


def get_clickhouse():
    """Get the ClickHouse client."""
    if not _client:
        raise RuntimeError("ClickHouse not initialized. Call init_clickhouse() first.")
    return _client


# ===== Analytics Event Logging =====

def log_match_event(
    user_hash: str,
    partner_hash: str,
    compatibility_score: float,
    interests_matched: List[str],
    conversation_duration: int,
    messages_exchanged: int,
    connection_type: str,
    outcome: str,
    quality_rating: Optional[int] = None,
) -> None:
    """Log a match event for analytics."""
    client = get_clickhouse()
    client.insert(
        "match_events",
        [[
            user_hash,
            partner_hash,
            compatibility_score,
            interests_matched,
            conversation_duration,
            messages_exchanged,
            quality_rating,
            connection_type,
            outcome,
        ]],
        column_names=[
            "user_hash", "partner_hash", "compatibility_score",
            "interests_matched", "conversation_duration_seconds",
            "messages_exchanged", "quality_rating", "connection_type", "outcome"
        ]
    )


def log_user_activity(
    user_hash: str,
    activity_type: str,
    interests: List[str],
    vibe: str,
    energy_level: int,
    session_duration: int,
    matches_accepted: int,
    matches_rejected: int,
    average_rating: float,
) -> None:
    """Log user activity for ML training."""
    client = get_clickhouse()
    client.insert(
        "user_activity",
        [[
            user_hash, activity_type, interests, vibe, energy_level,
            session_duration, matches_accepted, matches_rejected, average_rating
        ]],
        column_names=[
            "user_hash", "activity_type", "interests", "vibe", "energy_level",
            "session_duration_seconds", "matches_accepted", "matches_rejected",
            "average_rating"
        ]
    )


# ===== Analytics Queries =====

def get_matching_insights(days: int = 30) -> Dict[str, Any]:
    """Get matching algorithm insights for the last N days."""
    client = get_clickhouse()
    
    result = client.query(f"""
        SELECT
            avg(compatibility_score) as avg_compatibility,
            avg(conversation_duration_seconds) as avg_duration,
            avg(messages_exchanged) as avg_messages,
            countIf(outcome = 'completed') / count() as completion_rate,
            avg(quality_rating) as avg_quality
        FROM match_events
        WHERE timestamp > now() - INTERVAL {days} DAY
    """)
    
    row = result.first_row
    return {
        "avg_compatibility": row[0],
        "avg_duration_seconds": row[1],
        "avg_messages": row[2],
        "completion_rate": row[3],
        "avg_quality_rating": row[4],
    }


def get_popular_interests(limit: int = 20) -> List[Dict[str, Any]]:
    """Get the most popular interests."""
    client = get_clickhouse()
    
    result = client.query(f"""
        SELECT 
            interest,
            count() as count
        FROM user_activity
        ARRAY JOIN interests as interest
        WHERE timestamp > now() - INTERVAL 30 DAY
        GROUP BY interest
        ORDER BY count DESC
        LIMIT {limit}
    """)
    
    return [{"interest": row[0], "count": row[1]} for row in result.result_rows]
