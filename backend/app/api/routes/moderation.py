"""
Moderation routes - reporting, blocking, and safety.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.postgres import get_postgres_session
from app.models.schemas import (
    ReportCreate,
    ReportResponse,
    BlockRequest,
)
from app.models.database import User, Report, BlockedUser, ReportReason

router = APIRouter()


@router.post("/report", response_model=ReportResponse)
async def report_user(
    report: ReportCreate,
    anonymous_id: str,  # Would come from auth
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Report a user for violating community guidelines.
    
    Reports are reviewed by moderation team.
    """
    # Get reporter
    reporter_result = await db.execute(
        select(User).where(User.anonymous_id == anonymous_id)
    )
    reporter = reporter_result.scalar_one_or_none()
    
    if not reporter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Get reported user
    reported_result = await db.execute(
        select(User).where(User.anonymous_id == report.reported_anonymous_id)
    )
    reported = reported_result.scalar_one_or_none()
    
    if not reported:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reported user not found"
        )
    
    # Create report
    new_report = Report(
        reporter_id=reporter.id,
        reported_id=reported.id,
        reason=report.reason.value,
        description=report.description,
    )
    
    db.add(new_report)
    
    # Auto-actions for serious violations
    if report.reason == ReportReason.HATE_SPEECH:
        # Increase warning count
        reported.warning_count += 1
        
        # Auto-suspend if too many warnings
        if reported.warning_count >= 3:
            reported.is_banned = True
            reported.ban_reason = "Multiple reports for hate speech"
    
    await db.commit()
    await db.refresh(new_report)
    
    return ReportResponse(
        report_id=str(new_report.id),
        status="submitted",
        message="Report received. We'll review it shortly."
    )


@router.post("/block")
async def block_user(
    block: BlockRequest,
    anonymous_id: str,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Block a user.
    
    Blocked users cannot match with you or send messages.
    """
    # Get blocker
    blocker_result = await db.execute(
        select(User).where(User.anonymous_id == anonymous_id)
    )
    blocker = blocker_result.scalar_one_or_none()
    
    if not blocker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Get user to block
    blocked_result = await db.execute(
        select(User).where(User.anonymous_id == block.blocked_anonymous_id)
    )
    blocked = blocked_result.scalar_one_or_none()
    
    if not blocked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User to block not found"
        )
    
    # Check if already blocked
    existing = await db.execute(
        select(BlockedUser).where(
            BlockedUser.blocker_id == blocker.id,
            BlockedUser.blocked_id == blocked.id
        )
    )
    if existing.scalar_one_or_none():
        return {"status": "already_blocked"}
    
    # Create block
    new_block = BlockedUser(
        blocker_id=blocker.id,
        blocked_id=blocked.id,
        reason=block.reason,
    )
    
    db.add(new_block)
    await db.commit()
    
    return {"status": "blocked"}


@router.delete("/block/{blocked_anonymous_id}")
async def unblock_user(
    blocked_anonymous_id: str,
    anonymous_id: str,
    db: AsyncSession = Depends(get_postgres_session)
):
    """Unblock a user."""
    # Get blocker
    blocker_result = await db.execute(
        select(User).where(User.anonymous_id == anonymous_id)
    )
    blocker = blocker_result.scalar_one_or_none()
    
    if not blocker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Get blocked user
    blocked_result = await db.execute(
        select(User).where(User.anonymous_id == blocked_anonymous_id)
    )
    blocked = blocked_result.scalar_one_or_none()
    
    if not blocked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Find and delete block
    block_result = await db.execute(
        select(BlockedUser).where(
            BlockedUser.blocker_id == blocker.id,
            BlockedUser.blocked_id == blocked.id
        )
    )
    block = block_result.scalar_one_or_none()
    
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Block not found"
        )
    
    await db.delete(block)
    await db.commit()
    
    return {"status": "unblocked"}


@router.get("/blocked")
async def get_blocked_users(
    anonymous_id: str,
    db: AsyncSession = Depends(get_postgres_session)
):
    """Get list of blocked users."""
    # Get user
    user_result = await db.execute(
        select(User).where(User.anonymous_id == anonymous_id)
    )
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Get blocked users
    blocked_result = await db.execute(
        select(BlockedUser, User).join(
            User, BlockedUser.blocked_id == User.id
        ).where(BlockedUser.blocker_id == user.id)
    )
    
    blocked_list = [
        {
            "anonymous_id": blocked_user.anonymous_id,
            "blocked_at": blocked.created_at.isoformat(),
            "is_auto_block": blocked.is_auto_block,
        }
        for blocked, blocked_user in blocked_result.all()
    ]
    
    return {"blocked_users": blocked_list}
