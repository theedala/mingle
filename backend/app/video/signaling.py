"""
WebRTC Signaling Server for Video Chat.

Handles the signaling (offer/answer/ICE candidate exchange) for WebRTC
peer-to-peer video connections between matched users.
"""
from datetime import datetime
from typing import Dict, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json

from fastapi import WebSocket


class SignalType(str, Enum):
    """WebRTC signaling message types."""
    OFFER = "offer"
    ANSWER = "answer"
    ICE_CANDIDATE = "ice_candidate"
    VIDEO_READY = "video_ready"
    VIDEO_END = "video_end"
    BLUR_ON = "blur_on"
    BLUR_OFF = "blur_off"
    MUTE = "mute"
    UNMUTE = "unmute"


@dataclass
class VideoSession:
    """Active video session between two users."""
    match_id: str
    user_a_id: str
    user_b_id: str
    started_at: datetime = field(default_factory=datetime.utcnow)
    
    # Video state
    user_a_blur: bool = True  # Start with blur ON for privacy
    user_b_blur: bool = True
    user_a_muted: bool = False
    user_b_muted: bool = False
    user_a_ready: bool = False
    user_b_ready: bool = False
    
    def get_partner_id(self, user_id: str) -> Optional[str]:
        """Get the partner's user ID."""
        if user_id == self.user_a_id:
            return self.user_b_id
        elif user_id == self.user_b_id:
            return self.user_a_id
        return None
    
    def is_user_blurred(self, user_id: str) -> bool:
        """Check if a user has blur enabled."""
        if user_id == self.user_a_id:
            return self.user_a_blur
        return self.user_b_blur
    
    def set_blur(self, user_id: str, blur_on: bool) -> None:
        """Set blur state for a user."""
        if user_id == self.user_a_id:
            self.user_a_blur = blur_on
        else:
            self.user_b_blur = blur_on
    
    def set_ready(self, user_id: str, ready: bool) -> None:
        """Set ready state for a user."""
        if user_id == self.user_a_id:
            self.user_a_ready = ready
        else:
            self.user_b_ready = ready
    
    def both_ready(self) -> bool:
        """Check if both users are ready for video."""
        return self.user_a_ready and self.user_b_ready


class SignalingServer:
    """
    WebRTC signaling server.
    
    Manages WebSocket connections and routes signaling messages
    between peers for establishing video connections.
    """
    
    def __init__(self):
        # Active WebSocket connections: user_id -> WebSocket
        self.connections: Dict[str, WebSocket] = {}
        
        # Active video sessions: match_id -> VideoSession
        self.sessions: Dict[str, VideoSession] = {}
        
        # Pending ICE candidates: (match_id, user_id) -> List[candidates]
        self.pending_ice: Dict[tuple, list] = {}
    
    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        """Register a WebSocket connection for a user."""
        await websocket.accept()
        self.connections[user_id] = websocket
    
    def disconnect(self, user_id: str) -> None:
        """Remove a user's WebSocket connection."""
        self.connections.pop(user_id, None)
        
        # Clean up any sessions they were in
        for match_id, session in list(self.sessions.items()):
            if user_id in (session.user_a_id, session.user_b_id):
                del self.sessions[match_id]
    
    async def send_to_user(self, user_id: str, message: dict) -> bool:
        """Send a message to a specific user."""
        if user_id in self.connections:
            try:
                await self.connections[user_id].send_json(message)
                return True
            except Exception:
                self.disconnect(user_id)
                return False
        return False
    
    async def create_session(
        self, 
        match_id: str, 
        user_a_id: str, 
        user_b_id: str
    ) -> VideoSession:
        """Create a new video session for a match."""
        session = VideoSession(
            match_id=match_id,
            user_a_id=user_a_id,
            user_b_id=user_b_id,
        )
        self.sessions[match_id] = session
        
        # Notify both users that video session is ready
        await self.send_to_user(user_a_id, {
            "type": SignalType.VIDEO_READY.value,
            "match_id": match_id,
            "is_caller": True,  # User A will create the offer
        })
        await self.send_to_user(user_b_id, {
            "type": SignalType.VIDEO_READY.value,
            "match_id": match_id,
            "is_caller": False,  # User B will answer
        })
        
        return session
    
    async def handle_signal(
        self, 
        user_id: str, 
        match_id: str, 
        signal: dict
    ) -> None:
        """
        Handle a WebRTC signaling message.
        
        Routes offers, answers, and ICE candidates between peers.
        """
        session = self.sessions.get(match_id)
        if not session:
            return
        
        partner_id = session.get_partner_id(user_id)
        if not partner_id:
            return
        
        signal_type = signal.get("type")
        
        if signal_type == SignalType.OFFER.value:
            # Forward offer to partner
            await self.send_to_user(partner_id, {
                "type": SignalType.OFFER.value,
                "match_id": match_id,
                "sdp": signal.get("sdp"),
            })
            
            # Send any pending ICE candidates
            pending_key = (match_id, user_id)
            if pending_key in self.pending_ice:
                for candidate in self.pending_ice[pending_key]:
                    await self.send_to_user(partner_id, candidate)
                del self.pending_ice[pending_key]
        
        elif signal_type == SignalType.ANSWER.value:
            # Forward answer to partner
            await self.send_to_user(partner_id, {
                "type": SignalType.ANSWER.value,
                "match_id": match_id,
                "sdp": signal.get("sdp"),
            })
        
        elif signal_type == SignalType.ICE_CANDIDATE.value:
            # Forward ICE candidate to partner
            candidate_msg = {
                "type": SignalType.ICE_CANDIDATE.value,
                "match_id": match_id,
                "candidate": signal.get("candidate"),
            }
            
            # If partner not connected yet, queue the candidate
            if partner_id not in self.connections:
                pending_key = (match_id, user_id)
                if pending_key not in self.pending_ice:
                    self.pending_ice[pending_key] = []
                self.pending_ice[pending_key].append(candidate_msg)
            else:
                await self.send_to_user(partner_id, candidate_msg)
        
        elif signal_type == SignalType.BLUR_ON.value:
            session.set_blur(user_id, True)
            await self.send_to_user(partner_id, {
                "type": SignalType.BLUR_ON.value,
                "match_id": match_id,
            })
        
        elif signal_type == SignalType.BLUR_OFF.value:
            session.set_blur(user_id, False)
            await self.send_to_user(partner_id, {
                "type": SignalType.BLUR_OFF.value,
                "match_id": match_id,
            })
        
        elif signal_type == SignalType.MUTE.value:
            await self.send_to_user(partner_id, {
                "type": SignalType.MUTE.value,
                "match_id": match_id,
            })
        
        elif signal_type == SignalType.UNMUTE.value:
            await self.send_to_user(partner_id, {
                "type": SignalType.UNMUTE.value,
                "match_id": match_id,
            })
        
        elif signal_type == SignalType.VIDEO_END.value:
            await self.end_session(match_id, user_id)
    
    async def end_session(self, match_id: str, ended_by: str) -> None:
        """End a video session."""
        session = self.sessions.get(match_id)
        if not session:
            return
        
        partner_id = session.get_partner_id(ended_by)
        
        # Notify partner
        if partner_id:
            await self.send_to_user(partner_id, {
                "type": SignalType.VIDEO_END.value,
                "match_id": match_id,
            })
        
        # Clean up
        del self.sessions[match_id]
    
    def get_session(self, match_id: str) -> Optional[VideoSession]:
        """Get a video session by match ID."""
        return self.sessions.get(match_id)
    
    def get_session_stats(self) -> dict:
        """Get stats about active video sessions."""
        return {
            "active_connections": len(self.connections),
            "active_sessions": len(self.sessions),
        }


# Global signaling server instance
signaling_server = SignalingServer()
