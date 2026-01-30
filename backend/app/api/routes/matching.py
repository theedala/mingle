"""
Matching routes - finding and managing matches.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.postgres import get_postgres_session
from app.db.redis import get_redis
from app.models.schemas import (
    MatchRequest,
    MatchResult,
    UnmatchRequest,
    ConversationRating,
)
from app.models.database import User, Match, UnmatchedPair, BlockedUser
from app.matching.compatibility import UserProfile, calculate_compatibility
from app.matching.queue_manager import queue_manager

router = APIRouter()


@router.post("/find", response_model=MatchResult)
async def find_match(
    request: MatchRequest,
    anonymous_id: str,  # Would come from auth in production
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Find a compatible match for the user.
    
    Adds user to queue if no immediate match found.
    Returns match result with compatibility score.
    """
    # Get user profile
    result = await db.execute(
        select(User).where(User.anonymous_id == anonymous_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is temporarily suspended"
        )
    
    # Get blocked and unmatched users
    blocked_result = await db.execute(
        select(BlockedUser.blocked_id).where(BlockedUser.blocker_id == user.id)
    )
    blocked_by_result = await db.execute(
        select(BlockedUser.blocker_id).where(BlockedUser.blocked_id == user.id)
    )
    unmatched_result = await db.execute(
        select(UnmatchedPair.user2_id).where(UnmatchedPair.user1_id == user.id)
    )
    
    blocked_ids = [str(id) for id in blocked_result.scalars().all()]
    blocked_by_ids = [str(id) for id in blocked_by_result.scalars().all()]
    unmatched_ids = [str(id) for id in unmatched_result.scalars().all()]
    exclude_ids = blocked_ids + blocked_by_ids + unmatched_ids
    
    # Create user profile for matching
    profile = UserProfile(
        user_id=str(user.id),
        interests=user.interests,
        conversation_style=user.conversation_style,
        energy_level=user.energy_level,
        topics_to_avoid=user.topics_to_avoid,
        languages=user.languages,
        current_mood=request.mood or user.current_mood,
        reputation_score=user.reputation_score,
    )
    
    # Add to queue and try to find match
    await queue_manager.add_to_queue(
        str(user.id), 
        profile, 
        request.connection_type.value
    )
    
    # Try to find a match
    match_result = await queue_manager.find_match(
        str(user.id),
        blocked_ids=exclude_ids,
        unmatched_ids=unmatched_ids
    )
    
    if not match_result:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="Added to queue. Waiting for match..."
        )
    
    partner_id, compatibility = match_result
    
    # Create the match
    match_id = await queue_manager.create_match(
        str(user.id),
        partner_id,
        compatibility
    )
    
    # Get partner's anonymous ID
    partner_result = await db.execute(
        select(User.anonymous_id).where(User.id == partner_id)
    )
    partner_anonymous_id = partner_result.scalar_one_or_none() or "unknown"
    
    return MatchResult(
        match_id=match_id,
        partner_anonymous_id=partner_anonymous_id,
        compatibility_score=compatibility.score,
        interests_matched=compatibility.interest_overlap,
        connection_type=request.connection_type,
    )


@router.post("/unmatch")
async def unmatch(
    request: UnmatchRequest,
    anonymous_id: str,  # Would come from auth
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Unmatch from a conversation.
    
    Ends the match and optionally blocks the user.
    Users who unmatch won't be matched again.
    """
    # Get user
    result = await db.execute(
        select(User).where(User.anonymous_id == anonymous_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Get match info from Redis
    match_info = await queue_manager.get_match_info(request.match_id)
    if not match_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    # End the match
    await queue_manager.end_match(
        request.match_id,
        ended_by=str(user.id),
        reason="unmatched"
    )
    
    # Determine partner ID
    user_a = match_info.get("user_a")
    user_b = match_info.get("user_b")
    partner_id = user_b if user_a == str(user.id) else user_a
    
    # Record unmatch to prevent re-matching
    unmatch_record = UnmatchedPair(
        user1_id=user.id,
        user2_id=partner_id,
        unmatched_by=user.id,
        reason=request.reason
    )
    db.add(unmatch_record)
    
    # Optionally block the user
    if request.block_user:
        block = BlockedUser(
            blocker_id=user.id,
            blocked_id=partner_id,
            reason=request.reason
        )
        db.add(block)
    
    await db.commit()
    
    return {"status": "unmatched", "blocked": request.block_user}


@router.post("/rate")
async def rate_conversation(
    rating: ConversationRating,
    anonymous_id: str,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Rate a completed conversation.
    
    Ratings are anonymous and affect reputation scores.
    """
    # Get user
    result = await db.execute(
        select(User).where(User.anonymous_id == anonymous_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Get match info
    match_info = await queue_manager.get_match_info(rating.match_id)
    if not match_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    # Store rating in Redis for now (would also update DB match record)
    redis = get_redis()
    await redis.hset(
        f"match:{rating.match_id}",
        f"rating_{user.id}",
        str(rating.rating)
    )
    
    # Update partner's reputation based on rating
    user_a = match_info.get("user_a")
    user_b = match_info.get("user_b")
    partner_id = user_b if user_a == str(user.id) else user_a
    
    partner_result = await db.execute(
        select(User).where(User.id == partner_id)
    )
    partner = partner_result.scalar_one_or_none()
    
    if partner:
        if rating.rating >= 4:
            partner.positive_ratings += 1
            partner.reputation_score = min(100, partner.reputation_score + 0.5)
        elif rating.rating <= 2:
            partner.negative_ratings += 1
            partner.reputation_score = max(0, partner.reputation_score - 1)
        
        partner.total_conversations += 1
        await db.commit()
    
    return {"status": "rated", "rating": rating.rating}


@router.get("/queue/status")
async def get_queue_status(
    anonymous_id: str,
    db: AsyncSession = Depends(get_postgres_session)
):
    """Get status of user in match queue."""
    # Get user
    result = await db.execute(
        select(User).where(User.anonymous_id == anonymous_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Check if in queue
    redis = get_redis()
    in_queue = await redis.zscore("match_queue", str(user.id)) is not None
    queue_size = await queue_manager.get_queue_size()
    
    return {
        "in_queue": in_queue,
        "queue_size": queue_size,
        "estimated_wait": "1-3 minutes" if queue_size < 10 else "3-5 minutes"
    }


@router.delete("/queue/leave")
async def leave_queue(
    anonymous_id: str,
    db: AsyncSession = Depends(get_postgres_session)
):
    """Leave the match queue."""
    result = await db.execute(
        select(User).where(User.anonymous_id == anonymous_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    await queue_manager.remove_from_queue(str(user.id))
    
    return {"status": "left_queue"}
