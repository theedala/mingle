"""
Ice breaker games API routes.
"""
from typing import Optional, List
from fastapi import APIRouter
from pydantic import BaseModel

from app.chat.icebreakers import icebreaker_engine, GameType

router = APIRouter()


class GamePromptResponse(BaseModel):
    """Ice breaker prompt response."""
    game_type: str
    prompt: str
    options: Optional[List[str]] = None
    category: str


@router.get("/prompt/{match_id}", response_model=GamePromptResponse)
async def get_ice_breaker(
    match_id: str,
    game_type: Optional[str] = None,
    category: Optional[str] = None
):
    """
    Get a random ice breaker prompt for a match.
    
    Avoids repeating prompts within the same conversation.
    """
    # Parse game type if provided
    parsed_type = None
    if game_type:
        try:
            parsed_type = GameType(game_type)
        except ValueError:
            pass
    
    prompt = icebreaker_engine.get_random_prompt(match_id, parsed_type, category)
    
    return GamePromptResponse(
        game_type=prompt.game_type.value,
        prompt=prompt.prompt,
        options=prompt.options,
        category=prompt.category
    )


@router.get("/sequence/{match_id}", response_model=List[GamePromptResponse])
async def get_game_sequence(
    match_id: str,
    count: int = 5
):
    """
    Get a sequence of varied prompts for a game session.
    
    Great for a quick "get to know you" round.
    """
    prompts = icebreaker_engine.get_game_sequence(match_id, count)
    
    return [
        GamePromptResponse(
            game_type=p.game_type.value,
            prompt=p.prompt,
            options=p.options,
            category=p.category
        )
        for p in prompts
    ]


@router.get("/categories")
async def get_categories():
    """Get all available prompt categories."""
    return {
        "categories": icebreaker_engine.get_available_categories()
    }


@router.get("/types")
async def get_game_types():
    """Get all available game types."""
    return {
        "types": [t.value for t in GameType]
    }


@router.delete("/history/{match_id}")
async def clear_history(match_id: str):
    """Clear prompt history for a match (enables repeating prompts)."""
    icebreaker_engine.clear_match_history(match_id)
    return {"status": "history_cleared"}
