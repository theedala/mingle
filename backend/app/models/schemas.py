"""
Pydantic schemas for API request/response validation.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum


# ===== Enums =====

class ConversationStyle(str, Enum):
    CASUAL = "casual"
    DEEP = "deep"
    PLAYFUL = "playful"
    CHILL = "chill"


class EnergyLevel(str, Enum):
    EARLY_BIRD = "early_bird"
    NIGHT_OWL = "night_owl"
    FLEXIBLE = "flexible"


class ConnectionType(str, Enum):
    TEXT = "text"
    VIDEO = "video"


class ReportReason(str, Enum):
    HATE_SPEECH = "hate_speech"
    HARASSMENT = "harassment"
    SPAM = "spam"
    INAPPROPRIATE = "inappropriate"
    UNDERAGE = "underage"
    OTHER = "other"


# ===== User Schemas =====

class ProfileCreate(BaseModel):
    """Create an anonymous interest profile."""
    interests: List[str] = Field(..., min_length=1, max_length=20)
    conversation_style: ConversationStyle = ConversationStyle.CASUAL
    energy_level: EnergyLevel = EnergyLevel.FLEXIBLE
    topics_to_avoid: List[str] = Field(default_factory=list, max_length=10)
    languages: List[str] = Field(default=["en"], max_length=5)
    
    @field_validator("interests")
    @classmethod
    def validate_interests(cls, v):
        """Validate and normalize interests."""
        return [i.lower().strip() for i in v if len(i.strip()) >= 2]


class ProfileUpdate(BaseModel):
    """Update profile preferences."""
    interests: Optional[List[str]] = None
    conversation_style: Optional[ConversationStyle] = None
    energy_level: Optional[EnergyLevel] = None
    topics_to_avoid: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    current_mood: Optional[str] = Field(None, max_length=50)
    looking_for: Optional[str] = Field(None, max_length=100)


class ProfileResponse(BaseModel):
    """Anonymous profile response (no PII)."""
    anonymous_id: str
    interests: List[str]
    conversation_style: ConversationStyle
    energy_level: EnergyLevel
    languages: List[str]
    current_mood: Optional[str] = None
    looking_for: Optional[str] = None
    reputation_score: float
    total_conversations: int
    
    class Config:
        from_attributes = True


# ===== Matching Schemas =====

class MatchRequest(BaseModel):
    """Request to find a match."""
    connection_type: ConnectionType = ConnectionType.TEXT
    mood: Optional[str] = Field(None, max_length=50)


class MatchResult(BaseModel):
    """Match result with compatibility info."""
    match_id: str
    partner_anonymous_id: str
    compatibility_score: float
    interests_matched: List[str]
    connection_type: ConnectionType


class UnmatchRequest(BaseModel):
    """Request to unmatch from current conversation."""
    match_id: str
    reason: Optional[str] = Field(None, max_length=200)
    block_user: bool = False  # Also block the user


class ConversationRating(BaseModel):
    """Rate a conversation (1-5 stars)."""
    match_id: str
    rating: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = Field(None, max_length=500)


# ===== Moderation Schemas =====

class ReportCreate(BaseModel):
    """Report a user."""
    reported_anonymous_id: str
    reason: ReportReason
    description: Optional[str] = Field(None, max_length=1000)
    match_id: Optional[str] = None  # Link to conversation if applicable


class ReportResponse(BaseModel):
    """Report confirmation."""
    report_id: str
    status: str = "submitted"
    message: str = "Report received. We'll review it shortly."


class BlockRequest(BaseModel):
    """Block a user."""
    blocked_anonymous_id: str
    reason: Optional[str] = Field(None, max_length=200)


# ===== Chat Schemas =====

class MessageCreate(BaseModel):
    """Send a chat message."""
    content: str = Field(..., min_length=1, max_length=5000)
    ephemeral: bool = False  # Self-destructing message
    ephemeral_seconds: int = Field(default=60, ge=10, le=3600)


class MessageResponse(BaseModel):
    """Chat message response."""
    id: str
    sender_anonymous_id: str
    content: str
    timestamp: datetime
    ephemeral: bool = False
    expires_at: Optional[datetime] = None


class ReactionCreate(BaseModel):
    """Add reaction to a message."""
    message_id: str
    emoji: str = Field(..., max_length=10)


# ===== WebSocket Events =====

class WSEvent(BaseModel):
    """WebSocket event wrapper."""
    event: str
    data: dict


class TypingIndicator(BaseModel):
    """Typing indicator event."""
    is_typing: bool


# ===== Analytics Schemas =====

class MatchInsights(BaseModel):
    """Matching algorithm insights."""
    avg_compatibility: float
    avg_duration_seconds: float
    avg_messages: float
    completion_rate: float
    avg_quality_rating: Optional[float] = None


class PopularInterest(BaseModel):
    """Popular interest stats."""
    interest: str
    count: int
