"""
Profile routes - anonymous interest profile management.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_postgres_session
from app.core.security import generate_anonymous_id
from app.models.schemas import (
    ProfileCreate,
    ProfileUpdate,
    ProfileResponse,
)
from app.models.database import User

router = APIRouter()


@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Create a new anonymous profile.
    
    No personal information required - just interests and preferences.
    Returns an anonymous ID for future interactions.
    """
    # Generate anonymous ID
    anonymous_id = generate_anonymous_id()
    
    # Create user
    user = User(
        anonymous_id=anonymous_id,
        interests=profile_data.interests,
        conversation_style=profile_data.conversation_style.value,
        energy_level=profile_data.energy_level.value,
        topics_to_avoid=profile_data.topics_to_avoid,
        languages=profile_data.languages,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return ProfileResponse(
        anonymous_id=user.anonymous_id,
        interests=user.interests,
        conversation_style=profile_data.conversation_style,
        energy_level=profile_data.energy_level,
        languages=user.languages,
        reputation_score=user.reputation_score,
        total_conversations=user.total_conversations,
    )


@router.get("/{anonymous_id}", response_model=ProfileResponse)
async def get_profile(
    anonymous_id: str,
    db: AsyncSession = Depends(get_postgres_session)
):
    """Get a user's anonymous profile."""
    from sqlalchemy import select
    
    result = await db.execute(
        select(User).where(User.anonymous_id == anonymous_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return ProfileResponse(
        anonymous_id=user.anonymous_id,
        interests=user.interests,
        conversation_style=user.conversation_style,
        energy_level=user.energy_level,
        languages=user.languages,
        current_mood=user.current_mood,
        looking_for=user.looking_for,
        reputation_score=user.reputation_score,
        total_conversations=user.total_conversations,
    )


@router.patch("/{anonymous_id}", response_model=ProfileResponse)
async def update_profile(
    anonymous_id: str,
    profile_data: ProfileUpdate,
    db: AsyncSession = Depends(get_postgres_session)
):
    """Update profile preferences."""
    from sqlalchemy import select
    
    result = await db.execute(
        select(User).where(User.anonymous_id == anonymous_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Update fields that were provided
    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(user, field):
            if hasattr(value, 'value'):  # Enum
                setattr(user, field, value.value)
            else:
                setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    return ProfileResponse(
        anonymous_id=user.anonymous_id,
        interests=user.interests,
        conversation_style=user.conversation_style,
        energy_level=user.energy_level,
        languages=user.languages,
        current_mood=user.current_mood,
        looking_for=user.looking_for,
        reputation_score=user.reputation_score,
        total_conversations=user.total_conversations,
    )


@router.get("/{anonymous_id}/interests", response_model=List[str])
async def get_interests(
    anonymous_id: str,
    db: AsyncSession = Depends(get_postgres_session)
):
    """Get user's interests."""
    from sqlalchemy import select
    
    result = await db.execute(
        select(User.interests).where(User.anonymous_id == anonymous_id)
    )
    interests = result.scalar_one_or_none()
    
    if interests is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return interests
