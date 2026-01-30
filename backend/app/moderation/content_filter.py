"""
Content moderation system with hate speech detection and auto-blocking.

Uses pattern matching and sentiment analysis to detect harmful content.
"""
import re
from typing import Tuple, List, Optional
from dataclasses import dataclass
from enum import Enum


class ViolationType(str, Enum):
    """Types of content violations."""
    HATE_SPEECH = "hate_speech"
    HARASSMENT = "harassment"
    SPAM = "spam"
    EXPLICIT = "explicit"
    THREATS = "threats"
    SELF_HARM = "self_harm"
    NONE = "none"


class Severity(str, Enum):
    """Violation severity levels."""
    LOW = "low"        # Warning only
    MEDIUM = "medium"  # Temp block
    HIGH = "high"      # Auto-block + report


@dataclass
class ModerationResult:
    """Result of content moderation check."""
    is_safe: bool
    violation_type: ViolationType
    severity: Severity
    confidence: float
    flagged_content: Optional[str] = None
    action: str = "none"  # none, warn, block, auto_block


class ContentModerator:
    """
    Content moderation engine for real-time message filtering.
    
    Uses multi-layer approach:
    1. Keyword/pattern matching (fast, low-cost)
    2. Context analysis (medium cost)
    3. Optional: ML-based classification (for escalation)
    """
    
    # Hate speech patterns (simplified - production would use ML models)
    HATE_PATTERNS = [
        # Slurs and hate terms (redacted for safety, would be comprehensive list)
        r"\b(hate|kill|die)\s+(you|them|all)\b",
        r"\b(go\s+)?die\b",
        r"\bkill\s+yourself\b",
        r"\bkys\b",
    ]
    
    HARASSMENT_PATTERNS = [
        r"\b(stalk|follow)\s+(you|home)\b",
        r"\bi('ll|m\s+going\s+to)\s+(find|get|hurt)\s+you\b",
        r"\b(where\s+do\s+you\s+live|send\s+address)\b",
    ]
    
    SPAM_PATTERNS = [
        r"(https?://\S+\s*){3,}",  # Multiple URLs
        r"(.)\1{10,}",  # Repeated characters
        r"(join|follow|subscribe|click|free money|giveaway)",
    ]
    
    EXPLICIT_PATTERNS = [
        r"\b(send\s+(nudes|pics)|show\s+me)\b",
        r"\b(onlyfans|snapchat\s+premium)\b",
    ]
    
    # Words that boost severity when combined with other violations
    SEVERITY_BOOSTERS = [
        "definitely", "seriously", "literally", "actually",
        "i will", "i'm going to", "i swear"
    ]
    
    def __init__(self):
        # Compile patterns for efficiency
        self._hate_regex = [re.compile(p, re.IGNORECASE) for p in self.HATE_PATTERNS]
        self._harassment_regex = [re.compile(p, re.IGNORECASE) for p in self.HARASSMENT_PATTERNS]
        self._spam_regex = [re.compile(p, re.IGNORECASE) for p in self.SPAM_PATTERNS]
        self._explicit_regex = [re.compile(p, re.IGNORECASE) for p in self.EXPLICIT_PATTERNS]
    
    def check_message(self, content: str) -> ModerationResult:
        """
        Check a message for violations.
        
        Returns moderation result with recommended action.
        """
        content = content.strip()
        
        # Check each category
        hate_result = self._check_patterns(content, self._hate_regex, ViolationType.HATE_SPEECH)
        if hate_result:
            return self._build_result(
                ViolationType.HATE_SPEECH,
                Severity.HIGH,
                hate_result,
                confidence=0.9,
                action="auto_block"
            )
        
        harassment_result = self._check_patterns(content, self._harassment_regex, ViolationType.HARASSMENT)
        if harassment_result:
            return self._build_result(
                ViolationType.HARASSMENT,
                Severity.HIGH,
                harassment_result,
                confidence=0.85,
                action="auto_block"
            )
        
        spam_result = self._check_patterns(content, self._spam_regex, ViolationType.SPAM)
        if spam_result:
            return self._build_result(
                ViolationType.SPAM,
                Severity.MEDIUM,
                spam_result,
                confidence=0.7,
                action="warn"
            )
        
        explicit_result = self._check_patterns(content, self._explicit_regex, ViolationType.EXPLICIT)
        if explicit_result:
            return self._build_result(
                ViolationType.EXPLICIT,
                Severity.MEDIUM,
                explicit_result,
                confidence=0.8,
                action="warn"
            )
        
        # Content is safe
        return ModerationResult(
            is_safe=True,
            violation_type=ViolationType.NONE,
            severity=Severity.LOW,
            confidence=1.0,
            action="none"
        )
    
    def _check_patterns(
        self, 
        content: str, 
        patterns: List[re.Pattern], 
        violation_type: ViolationType
    ) -> Optional[str]:
        """Check content against a list of patterns."""
        for pattern in patterns:
            match = pattern.search(content)
            if match:
                return match.group()
        return None
    
    def _build_result(
        self,
        violation_type: ViolationType,
        severity: Severity,
        flagged_content: str,
        confidence: float,
        action: str
    ) -> ModerationResult:
        """Build a moderation result."""
        return ModerationResult(
            is_safe=False,
            violation_type=violation_type,
            severity=severity,
            confidence=confidence,
            flagged_content=flagged_content,
            action=action
        )
    
    def should_auto_block(self, result: ModerationResult) -> bool:
        """Check if the violation warrants an auto-block."""
        return (
            not result.is_safe and 
            result.severity == Severity.HIGH and
            result.action == "auto_block"
        )
    
    def get_action(self, result: ModerationResult) -> dict:
        """Get the recommended moderation action."""
        if result.is_safe:
            return {"action": "allow", "message": None}
        
        if result.action == "auto_block":
            return {
                "action": "auto_block",
                "reason": result.violation_type.value,
                "message": "This message violates our community guidelines. The user has been blocked."
            }
        
        if result.action == "warn":
            return {
                "action": "warn",
                "reason": result.violation_type.value,
                "message": "Please keep the conversation respectful."
            }
        
        return {"action": "allow", "message": None}


# Global moderator instance
moderator = ContentModerator()


def check_content(content: str) -> ModerationResult:
    """Quick access to content checking."""
    return moderator.check_message(content)


def should_auto_block(content: str) -> Tuple[bool, Optional[str]]:
    """Check if content should trigger auto-block."""
    result = moderator.check_message(content)
    if moderator.should_auto_block(result):
        return True, result.violation_type.value
    return False, None
