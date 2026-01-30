"""
Chat routes - messaging and real-time communication.
"""
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json

from app.db.postgres import get_postgres_session
from app.db.mongodb import get_messages_collection, get_conversations_collection
from app.db.redis import get_redis, publish_event
from app.models.schemas import MessageCreate, MessageResponse, ReactionCreate
from app.models.database import User, BlockedUser
from app.moderation.content_filter import check_content, should_auto_block
from app.matching.queue_manager import queue_manager

router = APIRouter()


# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for real-time chat."""
    
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)
    
    async def send_to_user(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)
    
    async def broadcast_to_match(self, match_id: str, message: dict, exclude_user: str = None):
        """Broadcast message to all users in a match."""
        match_info = await queue_manager.get_match_info(match_id)
        if match_info:
            for user_id in [match_info.get("user_a"), match_info.get("user_b")]:
                if user_id and user_id != exclude_user:
                    await self.send_to_user(user_id, message)


manager = ConnectionManager()


@router.websocket("/ws/{anonymous_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    anonymous_id: str,
):
    """
    WebSocket endpoint for real-time chat.
    
    Events:
    - message: Send/receive chat messages
    - typing: Typing indicators
    - reaction: Message reactions
    - match_end: Match ended notification
    """
    # Get user ID from anonymous ID (simplified - would use auth in production)
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
    
    await manager.connect(user_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            event_type = data.get("event")
            
            if event_type == "message":
                await handle_message(user_id, data, websocket)
            elif event_type == "typing":
                await handle_typing(user_id, data)
            elif event_type == "reaction":
                await handle_reaction(user_id, data)
            elif event_type == "ping":
                await websocket.send_json({"event": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect(user_id)


async def handle_message(user_id: str, data: dict, websocket: WebSocket):
    """Handle incoming chat message."""
    match_id = data.get("match_id")
    content = data.get("content", "")
    ephemeral = data.get("ephemeral", False)
    ephemeral_seconds = data.get("ephemeral_seconds", 60)
    
    if not match_id or not content:
        return
    
    # Check content moderation
    moderation_result = check_content(content)
    
    if not moderation_result.is_safe:
        # Check if should auto-block
        should_block, reason = should_auto_block(content)
        
        if should_block:
            # Auto-block the sender
            await websocket.send_json({
                "event": "moderation",
                "action": "blocked",
                "reason": reason,
                "message": "Your message violated our community guidelines. You have been blocked from this conversation."
            })
            
            # End the match
            await queue_manager.end_match(match_id, user_id, reason="auto_blocked")
            
            # Notify partner
            match_info = await queue_manager.get_match_info(match_id)
            if match_info:
                partner_id = match_info.get("user_b") if match_info.get("user_a") == user_id else match_info.get("user_a")
                await manager.send_to_user(partner_id, {
                    "event": "match_end",
                    "reason": "partner_violated_guidelines"
                })
            return
        else:
            # Just warn
            await websocket.send_json({
                "event": "moderation",
                "action": "warning",
                "message": "Please keep the conversation respectful."
            })
    
    # Store message in MongoDB
    messages = get_messages_collection()
    
    message_doc = {
        "match_id": match_id,
        "sender_id": user_id,
        "content": content,
        "timestamp": datetime.utcnow(),
        "ephemeral": ephemeral,
    }
    
    if ephemeral:
        message_doc["expires_at"] = datetime.utcnow() + timedelta(seconds=ephemeral_seconds)
    
    result = await messages.insert_one(message_doc)
    message_id = str(result.inserted_id)
    
    # Get sender's anonymous ID for broadcast
    from app.db.postgres import get_engine
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import text
    
    async with AsyncSession(get_engine()) as db:
        result = await db.execute(
            text("SELECT anonymous_id FROM users WHERE id = :uid"),
            {"uid": user_id}
        )
        row = result.fetchone()
        sender_anonymous_id = row[0] if row else "unknown"
    
    # Broadcast to match participants
    await manager.broadcast_to_match(match_id, {
        "event": "message",
        "message_id": message_id,
        "sender_anonymous_id": sender_anonymous_id,
        "content": content,
        "timestamp": datetime.utcnow().isoformat(),
        "ephemeral": ephemeral,
    })


async def handle_typing(user_id: str, data: dict):
    """Handle typing indicator."""
    match_id = data.get("match_id")
    is_typing = data.get("is_typing", False)
    
    if not match_id:
        return
    
    await manager.broadcast_to_match(match_id, {
        "event": "typing",
        "user_id": user_id,
        "is_typing": is_typing,
    }, exclude_user=user_id)


async def handle_reaction(user_id: str, data: dict):
    """Handle message reaction."""
    message_id = data.get("message_id")
    emoji = data.get("emoji")
    match_id = data.get("match_id")
    
    if not message_id or not emoji or not match_id:
        return
    
    # Store reaction in MongoDB
    from app.db.mongodb import get_reactions_collection
    reactions = get_reactions_collection()
    
    await reactions.update_one(
        {"message_id": message_id, "user_id": user_id},
        {"$set": {"emoji": emoji, "timestamp": datetime.utcnow()}},
        upsert=True
    )
    
    # Broadcast reaction
    await manager.broadcast_to_match(match_id, {
        "event": "reaction",
        "message_id": message_id,
        "user_id": user_id,
        "emoji": emoji,
    })


@router.get("/messages/{match_id}", response_model=List[MessageResponse])
async def get_messages(
    match_id: str,
    limit: int = 50,
    before: Optional[str] = None
):
    """Get chat messages for a match."""
    messages = get_messages_collection()
    
    query = {"match_id": match_id}
    if before:
        from bson import ObjectId
        query["_id"] = {"$lt": ObjectId(before)}
    
    cursor = messages.find(query).sort("timestamp", -1).limit(limit)
    
    result = []
    async for msg in cursor:
        result.append(MessageResponse(
            id=str(msg["_id"]),
            sender_anonymous_id=msg.get("sender_anonymous_id", "unknown"),
            content=msg["content"],
            timestamp=msg["timestamp"],
            ephemeral=msg.get("ephemeral", False),
            expires_at=msg.get("expires_at"),
        ))
    
    return list(reversed(result))


@router.get("/conversation/{match_id}")
async def get_conversation_info(match_id: str):
    """Get info about a conversation/match."""
    match_info = await queue_manager.get_match_info(match_id)
    
    if not match_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return {
        "match_id": match_id,
        "status": match_info.get("status", "unknown"),
        "compatibility_score": float(match_info.get("compatibility_score", 0)),
        "interests_matched": match_info.get("interests_matched", "").split(","),
        "created_at": match_info.get("created_at"),
    }
