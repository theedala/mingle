"""
SQLAlchemy models for PostgreSQL.

Defines user profiles, preferences, reputation, and moderation.
"""
from datetime import datetime
from typing import List, Optional
from enum import Enum as PyEnum
import uuid

from sqlalchemy import (
    String, Text, Integer, Float, Boolean, DateTime, 
    ForeignKey, Enum, ARRAY, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.postgres import Base


class ConversationStyle(str, PyEnum):
    """User's preferred conversation style."""
    CASUAL = "casual"
    DEEP = "deep"
    PLAYFUL = "playful"
    CHILL = "chill"


class EnergyLevel(str, PyEnum):
    """User's energy/activity pattern."""
    EARLY_BIRD = "early_bird"
    NIGHT_OWL = "night_owl"
    FLEXIBLE = "flexible"


class ModerationAction(str, PyEnum):
    """Moderation actions taken against users."""
    WARNING = "warning"
    TEMP_BAN = "temp_ban"
    PERM_BAN = "perm_ban"
    AUTO_BLOCK = "auto_block"


class ReportReason(str, PyEnum):
    """Reasons for reporting a user."""
    HATE_SPEECH = "hate_speech"
    HARASSMENT = "harassment"
    SPAM = "spam"
    INAPPROPRIATE = "inappropriate"
    UNDERAGE = "underage"
    OTHER = "other"


class User(Base):
    """
    User model - stores anonymous profile with interests.
    
    No PII stored - only interests and preferences for matching.
    """
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    anonymous_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    
    # Authentication (email is optional, hashed for privacy)
    email_hash: Mapped[Optional[str]] = mapped_column(String(64), unique=True, nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    
    # Anonymous profile - interests only, no identifying info
    interests: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    conversation_style: Mapped[str] = mapped_column(
        Enum(ConversationStyle), default=ConversationStyle.CASUAL
    )
    energy_level: Mapped[str] = mapped_column(
        Enum(EnergyLevel), default=EnergyLevel.FLEXIBLE
    )
    topics_to_avoid: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    languages: Mapped[List[str]] = mapped_column(ARRAY(String), default=["en"])
    
    # Mood (ephemeral, can change)
    current_mood: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    looking_for: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Reputation & Trust
    reputation_score: Mapped[float] = mapped_column(Float, default=50.0)  # 0-100
    total_conversations: Mapped[int] = mapped_column(Integer, default=0)
    positive_ratings: Mapped[int] = mapped_column(Integer, default=0)
    negative_ratings: Mapped[int] = mapped_column(Integer, default=0)
    
    # Moderation status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    ban_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ban_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    warning_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_active_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    blocked_users: Mapped[List["BlockedUser"]] = relationship(
        "BlockedUser", foreign_keys="BlockedUser.blocker_id", back_populates="blocker"
    )
    reports_made: Mapped[List["Report"]] = relationship(
        "Report", foreign_keys="Report.reporter_id", back_populates="reporter"
    )


class BlockedUser(Base):
    """
    Blocked users - prevents matching and messaging.
    
    Supports both manual blocks and auto-blocks from moderation.
    """
    __tablename__ = "blocked_users"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    blocker_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    blocked_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Block metadata
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_auto_block: Mapped[bool] = mapped_column(Boolean, default=False)  # System-generated
    auto_block_reason: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # hate_speech, etc.
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    blocker: Mapped["User"] = relationship("User", foreign_keys=[blocker_id])
    blocked: Mapped["User"] = relationship("User", foreign_keys=[blocked_id])


class Report(Base):
    """
    User reports for moderation.
    """
    __tablename__ = "reports"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reporter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    reported_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    reason: Mapped[str] = mapped_column(Enum(ReportReason))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evidence: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Message samples, etc.
    
    # Moderation status
    is_reviewed: Mapped[bool] = mapped_column(Boolean, default=False)
    action_taken: Mapped[Optional[str]] = mapped_column(Enum(ModerationAction), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    reporter: Mapped["User"] = relationship("User", foreign_keys=[reporter_id])
    reported: Mapped["User"] = relationship("User", foreign_keys=[reported_id])


class Match(Base):
    """
    Match history - tracks who was matched and outcomes.
    """
    __tablename__ = "matches"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user1_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    user2_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Match metrics
    compatibility_score: Mapped[float] = mapped_column(Float)
    interests_matched: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    
    # Connection details
    connection_type: Mapped[str] = mapped_column(String(10))  # text, video
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    messages_exchanged: Mapped[int] = mapped_column(Integer, default=0)
    
    # Outcome
    ended_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    end_reason: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # completed, skipped, unmatched, reported
    
    # Ratings (anonymous - only stored, not exposed to other user)
    user1_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5
    user2_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Relationships
    user1: Mapped["User"] = relationship("User", foreign_keys=[user1_id])
    user2: Mapped["User"] = relationship("User", foreign_keys=[user2_id])


class UnmatchedPair(Base):
    """
    Tracks unmatched pairs to prevent re-matching.
    
    Users who unmatch won't be matched again.
    """
    __tablename__ = "unmatched_pairs"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user1_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    user2_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    
    unmatched_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    reason: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
