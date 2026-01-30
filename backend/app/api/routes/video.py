"""
Video chat API routes - WebRTC signaling endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.postgres import get_postgres_session
from app.models.database import User
from app.matching.queue_manager import queue_manager
from app.video.signaling import signaling_server, SignalType

router = APIRouter()


@router.websocket("/signal/{anonymous_id}")
async def video_signaling(
    websocket: WebSocket,
    anonymous_id: str,
):
    """
    WebSocket endpoint for WebRTC signaling.
    
    Handles:
    - offer: SDP offer from caller
    - answer: SDP answer from callee
    - ice_candidate: ICE candidates for connection
    - blur_on/blur_off: Toggle camera blur
    - mute/unmute: Toggle audio
    - video_end: End video session
    """
    # Get user ID from anonymous ID
    from app.db.postgres import get_engine
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import text
    
    async with AsyncSession(get_engine()) as db:
        result = await db.execute(
            text("SELECT id FROM users WHERE anonymous_id = :aid"),
            {"aid": anonymous_id}
        )
        row = result.fetchone()
        if not row:
            await websocket.close(code=4001)
            return
        user_id = str(row[0])
    
    await signaling_server.connect(user_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            match_id = data.get("match_id")
            if not match_id:
                continue
            
            await signaling_server.handle_signal(user_id, match_id, data)
    
    except WebSocketDisconnect:
        signaling_server.disconnect(user_id)


@router.post("/start/{match_id}")
async def start_video_session(
    match_id: str,
    anonymous_id: str,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Initialize a video session for a match.
    
    Both users must have active WebSocket connections.
    Video starts with blur ON for privacy.
    """
    # Get match info
    match_info = await queue_manager.get_match_info(match_id)
    if not match_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    if match_info.get("status") != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Match is not active"
        )
    
    user_a_id = match_info.get("user_a")
    user_b_id = match_info.get("user_b")
    
    # Create video session
    session = await signaling_server.create_session(match_id, user_a_id, user_b_id)
    
    return {
        "status": "video_session_created",
        "match_id": match_id,
        "blur_enabled": True,  # Privacy default
    }


@router.post("/toggle-blur/{match_id}")
async def toggle_blur(
    match_id: str,
    blur_on: bool,
    anonymous_id: str,
    db: AsyncSession = Depends(get_postgres_session)
):
    """
    Toggle camera blur on/off.
    
    Users can reveal their video when trust is established.
    """
    # Get user ID
    result = await db.execute(
        select(User).where(User.anonymous_id == anonymous_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    session = signaling_server.get_session(match_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video session not found"
        )
    
    # Update blur state and notify partner
    signal_type = SignalType.BLUR_ON if blur_on else SignalType.BLUR_OFF
    await signaling_server.handle_signal(
        str(user.id),
        match_id,
        {"type": signal_type.value}
    )
    
    return {
        "status": "blur_updated",
        "blur_on": blur_on
    }


@router.post("/end/{match_id}")
async def end_video_session(
    match_id: str,
    anonymous_id: str,
    db: AsyncSession = Depends(get_postgres_session)
):
    """End a video session."""
    # Get user ID
    result = await db.execute(
        select(User).where(User.anonymous_id == anonymous_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    await signaling_server.end_session(match_id, str(user.id))
    
    return {"status": "video_ended"}


@router.get("/stats")
async def get_video_stats():
    """Get video session statistics."""
    return signaling_server.get_session_stats()
