"""
Queue Manager - Smart matching queue with compatibility-based ordering.

Manages the pool of users waiting for matches and finds optimal pairings.
"""
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass
from datetime import datetime
import asyncio

from app.matching.compatibility import (
    CompatibilityEngine, 
    UserProfile, 
    CompatibilityResult,
    compatibility_engine
)
from app.db.redis import (
    add_to_match_queue,
    remove_from_match_queue,
    get_match_queue,
    get_redis
)


@dataclass
class QueuedUser:
    """User waiting in the match queue."""
    user_id: str
    profile: UserProfile
    connection_type: str  # "text" or "video"
    queued_at: datetime
    priority_score: float = 0.0


@dataclass
class MatchPair:
    """A matched pair of users."""
    user_a: QueuedUser
    user_b: QueuedUser
    compatibility: CompatibilityResult
    match_id: str


class QueueManager:
    """
    Manages the matching queue and finds optimal pairs.
    
    Strategy:
    1. Users join queue with their profile
    2. When enough users are in queue, find best matches
    3. Prioritize by: wait time + compatibility score
    4. Exclude blocked/unmatched pairs
    """
    
    MINIMUM_COMPATIBILITY = 30.0  # Minimum score to match
    QUEUE_BATCH_SIZE = 50  # Max users to consider at once
    
    def __init__(self):
        self.engine = compatibility_engine
        self._profiles_cache: Dict[str, UserProfile] = {}
    
    async def add_to_queue(
        self, 
        user_id: str, 
        profile: UserProfile,
        connection_type: str = "text"
    ) -> None:
        """Add a user to the matching queue."""
        # Cache profile for quick access
        self._profiles_cache[user_id] = profile
        
        # Calculate priority score based on reputation and wait time
        priority = profile.reputation_score
        
        # Store in Redis sorted set
        await add_to_match_queue(user_id, priority)
        
        # Store connection type preference
        redis = get_redis()
        await redis.hset(f"queue_meta:{user_id}", mapping={
            "connection_type": connection_type,
            "queued_at": datetime.utcnow().isoformat()
        })
    
    async def remove_from_queue(self, user_id: str) -> None:
        """Remove a user from the matching queue."""
        await remove_from_match_queue(user_id)
        self._profiles_cache.pop(user_id, None)
        
        redis = get_redis()
        await redis.delete(f"queue_meta:{user_id}")
    
    async def find_match(
        self, 
        user_id: str,
        blocked_ids: List[str] = None,
        unmatched_ids: List[str] = None
    ) -> Optional[Tuple[str, CompatibilityResult]]:
        """
        Find the best match for a user.
        
        Args:
            user_id: The user looking for a match
            blocked_ids: Users to exclude (blocked)
            unmatched_ids: Users to exclude (previously unmatched)
        
        Returns:
            Tuple of (matched_user_id, compatibility_result) or None
        """
        blocked_ids = blocked_ids or []
        unmatched_ids = unmatched_ids or []
        exclude_ids = set(blocked_ids + unmatched_ids + [user_id])
        
        # Get user's profile
        user_profile = self._profiles_cache.get(user_id)
        if not user_profile:
            return None
        
        # Get user's connection type preference
        redis = get_redis()
        user_meta = await redis.hgetall(f"queue_meta:{user_id}")
        user_connection_type = user_meta.get("connection_type", "text")
        
        # Get candidates from queue
        queue_entries = await get_match_queue(limit=self.QUEUE_BATCH_SIZE)
        
        best_match: Optional[Tuple[str, CompatibilityResult]] = None
        best_score = 0
        
        for candidate_id, priority in queue_entries:
            # Skip excluded users
            if candidate_id in exclude_ids:
                continue
            
            # Get candidate profile
            candidate_profile = self._profiles_cache.get(candidate_id)
            if not candidate_profile:
                continue
            
            # Check connection type match
            candidate_meta = await redis.hgetall(f"queue_meta:{candidate_id}")
            if candidate_meta.get("connection_type") != user_connection_type:
                continue
            
            # Calculate compatibility
            result = self.engine.calculate_compatibility(user_profile, candidate_profile)
            
            # Check minimum threshold
            if not result.is_compatible or result.score < self.MINIMUM_COMPATIBILITY:
                continue
            
            # Factor in wait time (boost for users waiting longer)
            queued_at = candidate_meta.get("queued_at")
            if queued_at:
                wait_seconds = (datetime.utcnow() - datetime.fromisoformat(queued_at)).total_seconds()
                wait_bonus = min(10, wait_seconds / 60)  # Max 10 point bonus for waiting
                adjusted_score = result.score + wait_bonus
            else:
                adjusted_score = result.score
            
            # Track best match
            if adjusted_score > best_score:
                best_score = adjusted_score
                best_match = (candidate_id, result)
        
        return best_match
    
    async def create_match(
        self, 
        user_a_id: str, 
        user_b_id: str,
        compatibility: CompatibilityResult
    ) -> str:
        """
        Create a match between two users.
        
        Removes both from queue and returns match ID.
        """
        import uuid
        
        # Remove both users from queue
        await self.remove_from_queue(user_a_id)
        await self.remove_from_queue(user_b_id)
        
        # Generate match ID
        match_id = str(uuid.uuid4())
        
        # Store match info in Redis for real-time access
        redis = get_redis()
        await redis.hset(f"match:{match_id}", mapping={
            "user_a": user_a_id,
            "user_b": user_b_id,
            "compatibility_score": str(compatibility.score),
            "interests_matched": ",".join(compatibility.interest_overlap),
            "created_at": datetime.utcnow().isoformat(),
            "status": "active"
        })
        
        # Set expiry for match data (24 hours)
        await redis.expire(f"match:{match_id}", 86400)
        
        return match_id
    
    async def get_match_info(self, match_id: str) -> Optional[Dict]:
        """Get info about an active match."""
        redis = get_redis()
        match_data = await redis.hgetall(f"match:{match_id}")
        return match_data if match_data else None
    
    async def end_match(
        self, 
        match_id: str, 
        ended_by: str,
        reason: str = "completed"
    ) -> None:
        """End an active match."""
        redis = get_redis()
        await redis.hset(f"match:{match_id}", mapping={
            "status": "ended",
            "ended_by": ended_by,
            "end_reason": reason,
            "ended_at": datetime.utcnow().isoformat()
        })
    
    async def get_queue_size(self) -> int:
        """Get the current queue size."""
        redis = get_redis()
        return await redis.zcard("match_queue")


# Global queue manager instance
queue_manager = QueueManager()
