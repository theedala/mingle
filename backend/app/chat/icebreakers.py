"""
Ice Breaker Games - Interactive conversation starters.

Games and prompts to help users connect and have fun conversations.
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import random


class GameType(str, Enum):
    """Types of ice breaker games."""
    WOULD_YOU_RATHER = "would_you_rather"
    TWO_TRUTHS_ONE_LIE = "two_truths_one_lie"
    TWENTY_QUESTIONS = "twenty_questions"
    THIS_OR_THAT = "this_or_that"
    CONVERSATION_STARTER = "conversation_starter"
    RAPID_FIRE = "rapid_fire"


@dataclass
class GamePrompt:
    """A single game prompt."""
    game_type: GameType
    prompt: str
    options: Optional[List[str]] = None
    category: str = "general"


# Would You Rather questions
WOULD_YOU_RATHER = [
    GamePrompt(
        GameType.WOULD_YOU_RATHER,
        "Would you rather be able to fly or be invisible?",
        ["Fly", "Be invisible"],
        "superpowers"
    ),
    GamePrompt(
        GameType.WOULD_YOU_RATHER,
        "Would you rather live in a treehouse or a houseboat?",
        ["Treehouse", "Houseboat"],
        "lifestyle"
    ),
    GamePrompt(
        GameType.WOULD_YOU_RATHER,
        "Would you rather never use social media again or never watch another movie?",
        ["No social media", "No movies"],
        "entertainment"
    ),
    GamePrompt(
        GameType.WOULD_YOU_RATHER,
        "Would you rather have the ability to read minds or see the future?",
        ["Read minds", "See the future"],
        "superpowers"
    ),
    GamePrompt(
        GameType.WOULD_YOU_RATHER,
        "Would you rather travel to the past or the future?",
        ["Past", "Future"],
        "time"
    ),
    GamePrompt(
        GameType.WOULD_YOU_RATHER,
        "Would you rather be a famous musician or a famous actor?",
        ["Musician", "Actor"],
        "fame"
    ),
    GamePrompt(
        GameType.WOULD_YOU_RATHER,
        "Would you rather have unlimited money or unlimited time?",
        ["Unlimited money", "Unlimited time"],
        "life"
    ),
    GamePrompt(
        GameType.WOULD_YOU_RATHER,
        "Would you rather always be 10 minutes late or 20 minutes early?",
        ["10 min late", "20 min early"],
        "habits"
    ),
]

# This or That questions
THIS_OR_THAT = [
    GamePrompt(GameType.THIS_OR_THAT, "Coffee or Tea?", ["Coffee", "Tea"], "drinks"),
    GamePrompt(GameType.THIS_OR_THAT, "Morning or Night?", ["Morning", "Night"], "time"),
    GamePrompt(GameType.THIS_OR_THAT, "Beach or Mountains?", ["Beach", "Mountains"], "travel"),
    GamePrompt(GameType.THIS_OR_THAT, "Books or Movies?", ["Books", "Movies"], "entertainment"),
    GamePrompt(GameType.THIS_OR_THAT, "Cats or Dogs?", ["Cats", "Dogs"], "animals"),
    GamePrompt(GameType.THIS_OR_THAT, "Pizza or Burgers?", ["Pizza", "Burgers"], "food"),
    GamePrompt(GameType.THIS_OR_THAT, "Summer or Winter?", ["Summer", "Winter"], "seasons"),
    GamePrompt(GameType.THIS_OR_THAT, "Call or Text?", ["Call", "Text"], "communication"),
    GamePrompt(GameType.THIS_OR_THAT, "Sweet or Savory?", ["Sweet", "Savory"], "food"),
    GamePrompt(GameType.THIS_OR_THAT, "City or Countryside?", ["City", "Countryside"], "lifestyle"),
]

# Conversation starters
CONVERSATION_STARTERS = [
    GamePrompt(GameType.CONVERSATION_STARTER, "What's the best trip you've ever taken?", category="travel"),
    GamePrompt(GameType.CONVERSATION_STARTER, "If you could learn any skill instantly, what would it be?", category="skills"),
    GamePrompt(GameType.CONVERSATION_STARTER, "What's your go-to karaoke song?", category="music"),
    GamePrompt(GameType.CONVERSATION_STARTER, "What's the most interesting thing you've learned recently?", category="learning"),
    GamePrompt(GameType.CONVERSATION_STARTER, "If you had to eat one cuisine for the rest of your life, what would it be?", category="food"),
    GamePrompt(GameType.CONVERSATION_STARTER, "What's your favorite way to spend a lazy Sunday?", category="lifestyle"),
    GamePrompt(GameType.CONVERSATION_STARTER, "What show are you currently binge-watching?", category="entertainment"),
    GamePrompt(GameType.CONVERSATION_STARTER, "If you could have dinner with anyone, dead or alive, who would it be?", category="dreams"),
    GamePrompt(GameType.CONVERSATION_STARTER, "What's your unpopular opinion?", category="opinions"),
    GamePrompt(GameType.CONVERSATION_STARTER, "What's the best advice you've ever received?", category="wisdom"),
]

# Rapid fire questions (quick, fun questions)
RAPID_FIRE = [
    GamePrompt(GameType.RAPID_FIRE, "Favorite color?", category="basics"),
    GamePrompt(GameType.RAPID_FIRE, "Last song you listened to?", category="music"),
    GamePrompt(GameType.RAPID_FIRE, "Current mood in one emoji?", category="feelings"),
    GamePrompt(GameType.RAPID_FIRE, "Favorite snack?", category="food"),
    GamePrompt(GameType.RAPID_FIRE, "Dream vacation destination?", category="travel"),
    GamePrompt(GameType.RAPID_FIRE, "Morning person or night owl?", category="habits"),
    GamePrompt(GameType.RAPID_FIRE, "Favorite movie genre?", category="entertainment"),
    GamePrompt(GameType.RAPID_FIRE, "One word to describe yourself?", category="personality"),
]


class IceBreakerEngine:
    """
    Engine for generating and managing ice breaker games.
    """
    
    def __init__(self):
        self.all_prompts = {
            GameType.WOULD_YOU_RATHER: WOULD_YOU_RATHER,
            GameType.THIS_OR_THAT: THIS_OR_THAT,
            GameType.CONVERSATION_STARTER: CONVERSATION_STARTERS,
            GameType.RAPID_FIRE: RAPID_FIRE,
        }
        
        # Track used prompts per match to avoid repetition
        self.used_prompts: Dict[str, List[str]] = {}
    
    def get_random_prompt(
        self, 
        match_id: str,
        game_type: Optional[GameType] = None,
        category: Optional[str] = None
    ) -> GamePrompt:
        """
        Get a random ice breaker prompt.
        
        Avoids repeating prompts within the same match.
        """
        # Get pool of prompts
        if game_type:
            pool = self.all_prompts.get(game_type, [])
        else:
            # Mix all types
            pool = []
            for prompts in self.all_prompts.values():
                pool.extend(prompts)
        
        # Filter by category if specified
        if category:
            pool = [p for p in pool if p.category == category]
        
        # Filter out used prompts
        used = self.used_prompts.get(match_id, [])
        available = [p for p in pool if p.prompt not in used]
        
        # If all used, reset
        if not available:
            self.used_prompts[match_id] = []
            available = pool
        
        # Pick random prompt
        prompt = random.choice(available)
        
        # Track as used
        if match_id not in self.used_prompts:
            self.used_prompts[match_id] = []
        self.used_prompts[match_id].append(prompt.prompt)
        
        return prompt
    
    def get_game_sequence(self, match_id: str, count: int = 5) -> List[GamePrompt]:
        """Get a sequence of varied prompts for a game session."""
        prompts = []
        types = list(self.all_prompts.keys())
        
        for i in range(count):
            # Rotate through game types
            game_type = types[i % len(types)]
            prompt = self.get_random_prompt(match_id, game_type)
            prompts.append(prompt)
        
        return prompts
    
    def clear_match_history(self, match_id: str) -> None:
        """Clear prompt history for a match."""
        self.used_prompts.pop(match_id, None)
    
    def get_available_categories(self) -> List[str]:
        """Get all available categories."""
        categories = set()
        for prompts in self.all_prompts.values():
            for p in prompts:
                categories.add(p.category)
        return sorted(categories)
    
    def to_dict(self, prompt: GamePrompt) -> dict:
        """Convert prompt to dictionary for API response."""
        return {
            "game_type": prompt.game_type.value,
            "prompt": prompt.prompt,
            "options": prompt.options,
            "category": prompt.category,
        }


# Global ice breaker engine
icebreaker_engine = IceBreakerEngine()
