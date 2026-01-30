"""
Compatibility Engine - Multi-dimensional matching algorithm.

Calculates compatibility scores based on:
- Interest overlap (weighted by specificity)
- Conversation style similarity
- Energy level match
- Language compatibility
- Previous interaction feedback
"""
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import math


class ConversationStyle(str, Enum):
    CASUAL = "casual"
    DEEP = "deep"
    PLAYFUL = "playful"
    CHILL = "chill"


class EnergyLevel(str, Enum):
    EARLY_BIRD = "early_bird"
    NIGHT_OWL = "night_owl"
    FLEXIBLE = "flexible"


@dataclass
class UserProfile:
    """User profile for matching (anonymized)."""
    user_id: str
    interests: List[str]
    conversation_style: ConversationStyle
    energy_level: EnergyLevel
    topics_to_avoid: List[str]
    languages: List[str]
    current_mood: Optional[str] = None
    reputation_score: float = 50.0


@dataclass
class CompatibilityResult:
    """Result of compatibility calculation."""
    score: float  # 0-100
    interest_overlap: List[str]
    breakdown: Dict[str, float]
    is_compatible: bool


# Interest categories for weighted matching
INTEREST_CATEGORIES = {
    "gaming": ["gaming", "video games", "pc gaming", "console", "esports", "minecraft", "fortnite", "valorant", "league of legends"],
    "music": ["music", "hip hop", "rock", "pop", "jazz", "classical", "edm", "indie", "kpop", "concerts"],
    "movies": ["movies", "films", "cinema", "netflix", "anime", "horror", "comedy", "action", "documentaries"],
    "tech": ["technology", "coding", "programming", "ai", "startups", "crypto", "gadgets", "software"],
    "sports": ["sports", "football", "basketball", "soccer", "tennis", "gym", "fitness", "running"],
    "books": ["books", "reading", "fiction", "non-fiction", "fantasy", "sci-fi", "poetry", "manga"],
    "art": ["art", "painting", "photography", "design", "illustration", "digital art", "crafts"],
    "travel": ["travel", "adventure", "backpacking", "cities", "nature", "hiking", "camping"],
    "food": ["food", "cooking", "restaurants", "baking", "foodie", "cuisine", "coffee", "wine"],
    "social": ["socializing", "parties", "clubs", "friends", "networking", "community"],
}


class CompatibilityEngine:
    """
    Multi-dimensional compatibility scoring engine.
    
    Weights:
    - Interest overlap: 35%
    - Vibe/style similarity: 25%
    - Energy match: 15%
    - Language overlap: 10%
    - Mood alignment: 15%
    """
    
    INTEREST_WEIGHT = 0.35
    STYLE_WEIGHT = 0.25
    ENERGY_WEIGHT = 0.15
    LANGUAGE_WEIGHT = 0.10
    MOOD_WEIGHT = 0.15
    
    # Style compatibility matrix (how well styles match)
    STYLE_COMPATIBILITY = {
        (ConversationStyle.CASUAL, ConversationStyle.CASUAL): 1.0,
        (ConversationStyle.CASUAL, ConversationStyle.CHILL): 0.8,
        (ConversationStyle.CASUAL, ConversationStyle.PLAYFUL): 0.7,
        (ConversationStyle.CASUAL, ConversationStyle.DEEP): 0.4,
        (ConversationStyle.DEEP, ConversationStyle.DEEP): 1.0,
        (ConversationStyle.DEEP, ConversationStyle.CHILL): 0.6,
        (ConversationStyle.DEEP, ConversationStyle.PLAYFUL): 0.3,
        (ConversationStyle.PLAYFUL, ConversationStyle.PLAYFUL): 1.0,
        (ConversationStyle.PLAYFUL, ConversationStyle.CHILL): 0.7,
        (ConversationStyle.CHILL, ConversationStyle.CHILL): 1.0,
    }
    
    # Energy compatibility
    ENERGY_COMPATIBILITY = {
        (EnergyLevel.EARLY_BIRD, EnergyLevel.EARLY_BIRD): 1.0,
        (EnergyLevel.EARLY_BIRD, EnergyLevel.FLEXIBLE): 0.8,
        (EnergyLevel.EARLY_BIRD, EnergyLevel.NIGHT_OWL): 0.3,
        (EnergyLevel.NIGHT_OWL, EnergyLevel.NIGHT_OWL): 1.0,
        (EnergyLevel.NIGHT_OWL, EnergyLevel.FLEXIBLE): 0.8,
        (EnergyLevel.FLEXIBLE, EnergyLevel.FLEXIBLE): 0.9,
    }
    
    def calculate_compatibility(
        self, 
        user_a: UserProfile, 
        user_b: UserProfile
    ) -> CompatibilityResult:
        """Calculate overall compatibility between two users."""
        
        # Check for dealbreakers first
        if not self._check_language_overlap(user_a.languages, user_b.languages):
            return CompatibilityResult(
                score=0,
                interest_overlap=[],
                breakdown={"language_block": 0},
                is_compatible=False
            )
        
        # Check for avoided topics
        if self._has_avoided_topics(user_a, user_b):
            return CompatibilityResult(
                score=0,
                interest_overlap=[],
                breakdown={"topic_block": 0},
                is_compatible=False
            )
        
        # Calculate component scores
        interest_score, matched_interests = self._calculate_interest_score(
            user_a.interests, user_b.interests
        )
        style_score = self._calculate_style_score(
            user_a.conversation_style, user_b.conversation_style
        )
        energy_score = self._calculate_energy_score(
            user_a.energy_level, user_b.energy_level
        )
        language_score = self._calculate_language_score(
            user_a.languages, user_b.languages
        )
        mood_score = self._calculate_mood_score(
            user_a.current_mood, user_b.current_mood
        )
        
        # Calculate weighted score
        total_score = (
            interest_score * self.INTEREST_WEIGHT +
            style_score * self.STYLE_WEIGHT +
            energy_score * self.ENERGY_WEIGHT +
            language_score * self.LANGUAGE_WEIGHT +
            mood_score * self.MOOD_WEIGHT
        ) * 100
        
        # Apply reputation boost/penalty
        reputation_modifier = self._calculate_reputation_modifier(
            user_a.reputation_score, user_b.reputation_score
        )
        total_score = min(100, total_score * reputation_modifier)
        
        breakdown = {
            "interests": interest_score * 100,
            "style": style_score * 100,
            "energy": energy_score * 100,
            "language": language_score * 100,
            "mood": mood_score * 100,
            "reputation_modifier": reputation_modifier,
        }
        
        return CompatibilityResult(
            score=round(total_score, 1),
            interest_overlap=matched_interests,
            breakdown=breakdown,
            is_compatible=total_score >= 30  # Minimum threshold
        )
    
    def _calculate_interest_score(
        self, 
        interests_a: List[str], 
        interests_b: List[str]
    ) -> Tuple[float, List[str]]:
        """
        Calculate interest overlap score with category awareness.
        
        Exact matches score higher than category matches.
        """
        set_a = set(i.lower() for i in interests_a)
        set_b = set(i.lower() for i in interests_b)
        
        # Exact matches
        exact_matches = set_a & set_b
        
        # Category matches (same category but different interests)
        category_matches = set()
        for interest_a in set_a - exact_matches:
            for interest_b in set_b - exact_matches:
                if self._same_category(interest_a, interest_b):
                    category_matches.add(interest_a)
                    break
        
        # Score calculation
        total_unique = len(set_a | set_b)
        if total_unique == 0:
            return 0.5, []  # No interests = neutral
        
        # Exact matches worth 1.0, category matches worth 0.5
        match_score = len(exact_matches) + (len(category_matches) * 0.5)
        score = min(1.0, match_score / max(len(set_a), len(set_b)))
        
        return score, list(exact_matches)
    
    def _same_category(self, interest_a: str, interest_b: str) -> bool:
        """Check if two interests are in the same category."""
        for category, interests in INTEREST_CATEGORIES.items():
            if interest_a in interests and interest_b in interests:
                return True
        return False
    
    def _calculate_style_score(
        self, 
        style_a: ConversationStyle, 
        style_b: ConversationStyle
    ) -> float:
        """Calculate conversation style compatibility."""
        key = (style_a, style_b)
        reverse_key = (style_b, style_a)
        return self.STYLE_COMPATIBILITY.get(key, 
            self.STYLE_COMPATIBILITY.get(reverse_key, 0.5))
    
    def _calculate_energy_score(
        self, 
        energy_a: EnergyLevel, 
        energy_b: EnergyLevel
    ) -> float:
        """Calculate energy level compatibility."""
        key = (energy_a, energy_b)
        reverse_key = (energy_b, energy_a)
        return self.ENERGY_COMPATIBILITY.get(key,
            self.ENERGY_COMPATIBILITY.get(reverse_key, 0.5))
    
    def _calculate_language_score(
        self, 
        languages_a: List[str], 
        languages_b: List[str]
    ) -> float:
        """Calculate language compatibility."""
        set_a = set(l.lower() for l in languages_a)
        set_b = set(l.lower() for l in languages_b)
        overlap = set_a & set_b
        
        if not overlap:
            return 0
        
        # More shared languages = higher score
        return min(1.0, len(overlap) * 0.5)
    
    def _check_language_overlap(
        self, 
        languages_a: List[str], 
        languages_b: List[str]
    ) -> bool:
        """Check if users share at least one language."""
        set_a = set(l.lower() for l in languages_a)
        set_b = set(l.lower() for l in languages_b)
        return bool(set_a & set_b)
    
    def _calculate_mood_score(
        self, 
        mood_a: Optional[str], 
        mood_b: Optional[str]
    ) -> float:
        """Calculate mood alignment score."""
        if not mood_a or not mood_b:
            return 0.5  # Neutral if no mood set
        
        # Simple match for now - could use NLP similarity
        if mood_a.lower() == mood_b.lower():
            return 1.0
        
        # Check for similar moods
        chill_moods = {"chill", "relaxed", "calm", "laid back"}
        energetic_moods = {"energetic", "excited", "hyped", "pumped"}
        deep_moods = {"deep", "thoughtful", "philosophical", "reflective"}
        
        mood_a_lower = mood_a.lower()
        mood_b_lower = mood_b.lower()
        
        for mood_group in [chill_moods, energetic_moods, deep_moods]:
            if mood_a_lower in mood_group and mood_b_lower in mood_group:
                return 0.8
        
        return 0.4
    
    def _has_avoided_topics(
        self, 
        user_a: UserProfile, 
        user_b: UserProfile
    ) -> bool:
        """Check if users have conflicting avoided topics."""
        # If user A avoids a topic that user B is interested in
        set_avoid_a = set(t.lower() for t in user_a.topics_to_avoid)
        set_interest_b = set(i.lower() for i in user_b.interests)
        
        set_avoid_b = set(t.lower() for t in user_b.topics_to_avoid)
        set_interest_a = set(i.lower() for i in user_a.interests)
        
        return bool(set_avoid_a & set_interest_b) or bool(set_avoid_b & set_interest_a)
    
    def _calculate_reputation_modifier(
        self, 
        rep_a: float, 
        rep_b: float
    ) -> float:
        """
        Calculate reputation-based modifier.
        
        Users with good reputation get slight boost, bad reputation penalty.
        """
        avg_rep = (rep_a + rep_b) / 2
        
        if avg_rep >= 70:
            return 1.1  # 10% boost
        elif avg_rep >= 50:
            return 1.0  # Neutral
        elif avg_rep >= 30:
            return 0.9  # 10% penalty
        else:
            return 0.8  # 20% penalty


# Global engine instance
compatibility_engine = CompatibilityEngine()


def calculate_compatibility(user_a: UserProfile, user_b: UserProfile) -> CompatibilityResult:
    """Quick access to compatibility calculation."""
    return compatibility_engine.calculate_compatibility(user_a, user_b)
