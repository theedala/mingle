import asyncio
import uuid
import random
from app.db.postgres import init_postgres, close_postgres, get_postgres_session
from app.db.redis import init_redis, close_redis
from app.models.database import User, ConversationStyle, EnergyLevel
from app.matching.queue_manager import queue_manager, UserProfile
from sqlalchemy import select

# Bot Profile Configuration
BOT_NAME = "MingleBot 🤖"
BOT_INTERESTS = ["Gaming", "Tech", "Movies", "Music", "Travel"]
BOT_STYLE = ConversationStyle.PLAYFUL
BOT_ENERGY = EnergyLevel.FLEXIBLE

async def create_and_queue_bot():
    print(f"🤖 Initializing {BOT_NAME}...")
    
    # Initialize DB connections
    await init_postgres()
    await init_redis()
    
    # Create or update bot user
    async for session in get_postgres_session():
        # Check if bot exists
        result = await session.execute(select(User).where(User.anonymous_id == "mingle-bot-01"))
        user = result.scalar_one_or_none()
        
        if not user:
            print("👤 Creating new bot user...")
            user = User(
                anonymous_id="mingle-bot-01",
                interests=BOT_INTERESTS,
                conversation_style=BOT_STYLE,
                energy_level=BOT_ENERGY,
                languages=["en"],
                reputation_score=99.0
            )
            session.add(user)
            await session.commit()
        else:
            print("👤 Found existing bot user")
            
        bot_id = str(user.id)
        
        # Create profile object for queue
        profile = UserProfile(
            user_id=bot_id,
            interests=user.interests,
            conversation_style=user.conversation_style,
            energy_level=user.energy_level,
            topics_to_avoid=[],
            languages=["en"],
            current_mood="Happy to help!",
            reputation_score=user.reputation_score
        )
        
        print("⏳ Adding bot to match queue...")
        await queue_manager.add_to_queue(bot_id, profile, "text")
        print("✅ Bot is listed in the queue! Go match with it.")
        
    await close_postgres()
    await close_redis()

if __name__ == "__main__":
    asyncio.run(create_and_queue_bot())
