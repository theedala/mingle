"""
Tests for the content moderation system.
"""
import pytest
from app.moderation.content_filter import (
    ContentModerator,
    ViolationType,
    Severity,
    check_content,
    should_auto_block,
)


@pytest.fixture
def moderator():
    return ContentModerator()


class TestContentModerator:
    """Tests for content moderation."""
    
    def test_safe_message_passes(self, moderator):
        """Normal messages should pass moderation."""
        result = moderator.check_message("Hey! How's it going? I love gaming too!")
        
        assert result.is_safe
        assert result.violation_type == ViolationType.NONE
        assert result.action == "none"
    
    def test_hate_speech_detected(self, moderator):
        """Hate speech should be detected and trigger auto-block."""
        result = moderator.check_message("I hate you, go die")
        
        assert not result.is_safe
        assert result.violation_type == ViolationType.HATE_SPEECH
        assert result.severity == Severity.HIGH
        assert result.action == "auto_block"
    
    def test_kys_detected(self, moderator):
        """KYS should be detected as hate speech."""
        result = moderator.check_message("kys")
        
        assert not result.is_safe
        assert result.violation_type == ViolationType.HATE_SPEECH
        assert result.action == "auto_block"
    
    def test_harassment_detected(self, moderator):
        """Harassment/threats should be detected."""
        result = moderator.check_message("I'll find you and hurt you")
        
        assert not result.is_safe
        assert result.violation_type == ViolationType.HARASSMENT
        assert result.action == "auto_block"
    
    def test_spam_detected(self, moderator):
        """Spam patterns should be detected with warning."""
        result = moderator.check_message("Click here for free money giveaway!")
        
        assert not result.is_safe
        assert result.violation_type == ViolationType.SPAM
        assert result.action == "warn"
    
    def test_explicit_requests_detected(self, moderator):
        """Explicit requests should be detected."""
        result = moderator.check_message("Send nudes")
        
        assert not result.is_safe
        assert result.violation_type == ViolationType.EXPLICIT
        assert result.action == "warn"
    
    def test_should_auto_block_logic(self, moderator):
        """should_auto_block should return True for serious violations."""
        hate_result = moderator.check_message("I hate you, die")
        safe_result = moderator.check_message("Hello!")
        spam_result = moderator.check_message("Free giveaway click now")
        
        assert moderator.should_auto_block(hate_result)
        assert not moderator.should_auto_block(safe_result)
        assert not moderator.should_auto_block(spam_result)  # Spam is warning only
    
    def test_helper_functions(self):
        """Test the helper functions."""
        result = check_content("Normal message")
        assert result.is_safe
        
        should_block, reason = should_auto_block("kill yourself")
        assert should_block
        assert reason == "hate_speech"
        
        should_block, reason = should_auto_block("Hello friend!")
        assert not should_block
        assert reason is None
    
    def test_get_action(self, moderator):
        """Test action recommendations."""
        hate_result = moderator.check_message("die")
        action = moderator.get_action(hate_result)
        
        assert action["action"] == "auto_block"
        assert "message" in action
        
        safe_result = moderator.check_message("Hi!")
        action = moderator.get_action(safe_result)
        
        assert action["action"] == "allow"
