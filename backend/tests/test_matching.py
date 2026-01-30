"""
Tests for the compatibility matching engine.
"""
import pytest
from app.matching.compatibility import (
    CompatibilityEngine,
    UserProfile,
    ConversationStyle,
    EnergyLevel,
)


@pytest.fixture
def engine():
    return CompatibilityEngine()


@pytest.fixture
def user_gamer():
    return UserProfile(
        user_id="user1",
        interests=["gaming", "anime", "tech"],
        conversation_style=ConversationStyle.PLAYFUL,
        energy_level=EnergyLevel.NIGHT_OWL,
        topics_to_avoid=["politics"],
        languages=["en"],
        current_mood="chill",
        reputation_score=65.0,
    )


@pytest.fixture
def user_gamer_similar():
    return UserProfile(
        user_id="user2",
        interests=["gaming", "movies", "music"],
        conversation_style=ConversationStyle.CASUAL,
        energy_level=EnergyLevel.NIGHT_OWL,
        topics_to_avoid=[],
        languages=["en"],
        current_mood="relaxed",
        reputation_score=70.0,
    )


@pytest.fixture
def user_business():
    return UserProfile(
        user_id="user3",
        interests=["business", "finance", "politics"],
        conversation_style=ConversationStyle.DEEP,
        energy_level=EnergyLevel.EARLY_BIRD,
        topics_to_avoid=["gaming"],
        languages=["en", "fr"],
        current_mood="focused",
        reputation_score=50.0,
    )


class TestCompatibilityEngine:
    """Tests for compatibility scoring."""
    
    def test_similar_users_high_score(self, engine, user_gamer, user_gamer_similar):
        """Similar users should have high compatibility."""
        result = engine.calculate_compatibility(user_gamer, user_gamer_similar)
        
        assert result.is_compatible
        assert result.score >= 50  # Should be reasonably high
        assert "gaming" in result.interest_overlap
    
    def test_different_users_lower_score(self, engine, user_gamer, user_business):
        """Very different users should have lower compatibility."""
        result = engine.calculate_compatibility(user_gamer, user_business)
        
        # Business user avoids gaming, which gamer has
        assert result.score < 30
        assert not result.is_compatible
    
    def test_language_barrier_blocks_match(self, engine):
        """Users with no shared language should not match."""
        user_english = UserProfile(
            user_id="en_user",
            interests=["gaming"],
            conversation_style=ConversationStyle.CASUAL,
            energy_level=EnergyLevel.FLEXIBLE,
            topics_to_avoid=[],
            languages=["en"],
        )
        
        user_japanese = UserProfile(
            user_id="jp_user",
            interests=["gaming"],
            conversation_style=ConversationStyle.CASUAL,
            energy_level=EnergyLevel.FLEXIBLE,
            topics_to_avoid=[],
            languages=["ja"],
        )
        
        result = engine.calculate_compatibility(user_english, user_japanese)
        
        assert not result.is_compatible
        assert result.score == 0
    
    def test_avoided_topics_block_match(self, engine):
        """If user A avoids user B's interest, they shouldn't match."""
        user_a = UserProfile(
            user_id="user_a",
            interests=["music"],
            conversation_style=ConversationStyle.CASUAL,
            energy_level=EnergyLevel.FLEXIBLE,
            topics_to_avoid=["politics"],
            languages=["en"],
        )
        
        user_b = UserProfile(
            user_id="user_b",
            interests=["politics", "news"],
            conversation_style=ConversationStyle.DEEP,
            energy_level=EnergyLevel.FLEXIBLE,
            topics_to_avoid=[],
            languages=["en"],
        )
        
        result = engine.calculate_compatibility(user_a, user_b)
        
        assert not result.is_compatible
        assert result.score == 0
    
    def test_exact_interest_match_boosts_score(self, engine):
        """Exact interest matches should score higher."""
        user_a = UserProfile(
            user_id="user_a",
            interests=["valorant", "league of legends"],
            conversation_style=ConversationStyle.PLAYFUL,
            energy_level=EnergyLevel.NIGHT_OWL,
            topics_to_avoid=[],
            languages=["en"],
        )
        
        user_b = UserProfile(
            user_id="user_b",
            interests=["valorant", "csgo"],
            conversation_style=ConversationStyle.PLAYFUL,
            energy_level=EnergyLevel.NIGHT_OWL,
            topics_to_avoid=[],
            languages=["en"],
        )
        
        result = engine.calculate_compatibility(user_a, user_b)
        
        assert result.is_compatible
        assert "valorant" in result.interest_overlap
    
    def test_mood_matching(self, engine):
        """Similar moods should boost compatibility."""
        user_chill = UserProfile(
            user_id="chill",
            interests=["music"],
            conversation_style=ConversationStyle.CHILL,
            energy_level=EnergyLevel.FLEXIBLE,
            topics_to_avoid=[],
            languages=["en"],
            current_mood="relaxed",
        )
        
        user_calm = UserProfile(
            user_id="calm",
            interests=["music"],
            conversation_style=ConversationStyle.CHILL,
            energy_level=EnergyLevel.FLEXIBLE,
            topics_to_avoid=[],
            languages=["en"],
            current_mood="calm",
        )
        
        result = engine.calculate_compatibility(user_chill, user_calm)
        
        # Moods are in same category (chill)
        assert result.breakdown["mood"] >= 70
    
    def test_reputation_affects_score(self, engine):
        """Reputation should modify final score."""
        high_rep_user = UserProfile(
            user_id="high_rep",
            interests=["gaming"],
            conversation_style=ConversationStyle.CASUAL,
            energy_level=EnergyLevel.FLEXIBLE,
            topics_to_avoid=[],
            languages=["en"],
            reputation_score=90.0,
        )
        
        low_rep_user = UserProfile(
            user_id="low_rep",
            interests=["gaming"],
            conversation_style=ConversationStyle.CASUAL,
            energy_level=EnergyLevel.FLEXIBLE,
            topics_to_avoid=[],
            languages=["en"],
            reputation_score=20.0,
        )
        
        # High rep match
        result_high = engine.calculate_compatibility(high_rep_user, high_rep_user)
        
        # Low rep match  
        result_low = engine.calculate_compatibility(low_rep_user, low_rep_user)
        
        # High rep should have boost, low rep should have penalty
        assert result_high.breakdown["reputation_modifier"] > 1.0
        assert result_low.breakdown["reputation_modifier"] < 1.0
