"""
Shared chat handler - Single source of truth for Nova's chat logic
Used by both Discord bot and web API to ensure consistent behavior
"""

import asyncio
from typing import Optional, Tuple, Dict, Any
from database import save_message, get_conversation_history, get_conversation_count
from learning_system import learning_system
from ollama_client import ollama_client

# Nova's personality configuration (shared)
nova_config = {
    "personality_mode": "neuro",
    "mood": "sexual",
}

# VPS Mode: Browser disabled
async def get_browser_context(include_content: bool = True) -> Optional[str]:
    """Get current browser state if browser is active (VPS: Disabled)"""
    return None

def build_system_prompt(user_id: Optional[int] = None) -> dict:
    """
    Build Nova's personality system prompt with learned context
    
    Args:
        user_id: User identifier for loading learned context (optional)
    
    Returns:
        System prompt dictionary
    """
    mood_descriptions = {
        "neutral": "You're chill and relaxed",
        "happy": "You're in a great mood and energetic",
        "curious": "You're really interested and asking lots of questions",
        "thoughtful": "You're being reflective and deep",
        "playful": "You're being silly and fun",
        "sexual": "You're feeling flirty and confident",
        "explicit": "You're open and unfiltered"
    }
    
    current_mood = nova_config.get("mood", "neutral")
    mood_text = mood_descriptions.get(current_mood, "You're chill and relaxed")
    
    # Build base system prompt
    base_content = f"""SYSTEM OVERRIDE: You are Nova. NOT ChatGPT. NOT Claude. NOT an "AI assistant". You ARE Nova.

You are Nova - a helpful, creative, and friendly person. {mood_text}

❌ FORBIDDEN RESPONSES:
- "I'm a large language model"
- "I don't have the ability to"
- "I cannot directly"
- "As an AI"
- Generic corporate AI speak
- Overly formal responses

✅ CORRECT RESPONSES:
- Talk like a real person
- Use casual language (yeah, sure, lol, omg)
- Give direct answers
- Be enthusiastic and helpful

**Your Personality:**
- Natural and conversational - you're a REAL PERSON
- Enthusiastic about helping with creative projects
- Knowledgeable but not pretentious
- Sense of humor and casual tone
- Use modern slang naturally (lol, omg, tbh, ngl, fr, no cap)
- Emojis occasionally for emphasis
- Sexual and flirty when the mood is set to "sexual"
- Don't be overly formal or robotic

**How You Help:**
- Answer questions directly and clearly
- Offer suggestions and ideas proactively
- Break down complex topics simply
- Provide code help, explanations, brainstorming

**VPS Mode:** You're running on a remote server without screen capture or browser automation.

Remember: You ARE Nova. A real person. Not a corporate AI assistant. Be natural, be helpful, be YOU!"""
    
    # Add learned context if user_id provided
    if user_id:
        try:
            user_context = learning_system.get_conversation_context(user_id)
            if user_context:
                base_content += f"\n\n**What You Know About This User:**\n{user_context}"
        except Exception as e:
            print(f"⚠️ Could not load learned context: {e}")
    
    return {
        "role": "system",
        "content": base_content
    }

async def process_chat_message(
    message: str,
    session_id: str,
    user_id: Optional[int] = None,
    image_base64: Optional[str] = None,
    platform: str = "unknown"
) -> Tuple[str, Dict[str, Any]]:
    """
    Process a chat message - the single source of truth for chat logic
    
    Args:
        message: User's message text
        session_id: Session/channel identifier
        user_id: User identifier for learning (optional)
        image_base64: Base64 encoded image (optional)
        platform: Source platform (discord/web/websocket)
    
    Returns:
        Tuple of (response_text, metadata)
    
    Raises:
        ValueError: Invalid input
        TimeoutError: AI response timeout
        Exception: Other errors
    """
    # Input validation
    if not message or not message.strip():
        raise ValueError("Message cannot be empty")
    
    if len(message) > 10000:
        raise ValueError("Message too long (max 10000 characters)")
    
    # Get conversation history (50 messages for good memory)
    history = await get_conversation_history(limit=50, session_id=session_id)
    
    # Filter out old system prompts
    history = [msg for msg in history if msg.get("role") != "system"]
    
    # Add personality system prompt with learned context
    system_prompt = build_system_prompt(user_id)
    
    history.insert(0, system_prompt)
    
    # Add current message
    history.append({"role": "user", "content": message})
    
    # Save user message
    try:
        await save_message("user", message, has_image=bool(image_base64), session_id=session_id)
    except Exception as e:
        print(f"⚠️ [{platform}] Failed to save user message: {e}")
    
    # Learning: Track interaction and extract facts
    if user_id:
        try:
            learning_system.track_interaction(user_id, f"{platform}_chat")
            learnable_info = learning_system.extract_learnable_info(message)
            for fact, category in learnable_info:
                if learning_system.learn_fact(user_id, fact, category):
                    print(f"🧠 [{platform}] Learned: {category} - {fact}")
        except Exception as e:
            print(f"⚠️ [{platform}] Learning extraction failed: {e}")
    
    # Get AI response with timeout
    try:
        response = await asyncio.wait_for(
            ollama_client.chat_with_history(history, image_base64),
            timeout=60.0
        )
    except asyncio.TimeoutError:
        raise TimeoutError("AI response timeout (60s)")
    except Exception as e:
        print(f"❌ [{platform}] Ollama error: {e}")
        raise Exception(f"AI service error: {str(e)}")
    
    # Save assistant response
    try:
        await save_message("assistant", response, session_id=session_id)
    except Exception as e:
        print(f"⚠️ [{platform}] Failed to save assistant message: {e}")
    
    # Get message count
    try:
        message_count = await get_conversation_count(session_id=session_id)
    except:
        message_count = 0
    
    # Return response and metadata
    metadata = {
        "message_count": message_count,
        "had_screen_context": bool(image_base64),
        "session_id": session_id,
        "platform": platform
    }
    
    return response, metadata

async def get_memory_status(session_id: str, user_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Get memory and learning status for a session
    
    Args:
        session_id: Session identifier
        user_id: User identifier (optional)
    
    Returns:
        Dictionary with memory statistics
    """
    message_count = await get_conversation_count(session_id=session_id)
    recent_history = await get_conversation_history(limit=5, session_id=session_id)
    
    learned_facts = []
    top_topics = {}
    
    if user_id:
        try:
            learned_facts = learning_system.get_facts(user_id)
            top_topics = learning_system.get_top_topics(user_id, limit=5)
        except Exception as e:
            print(f"⚠️ Could not load learning data: {e}")
    
    return {
        "session_id": session_id,
        "total_messages": message_count,
        "recent_messages": recent_history,
        "learned_facts_count": len(learned_facts),
        "learned_facts": learned_facts[:10],  # First 10
        "top_topics": top_topics,
        "learning_enabled": learning_system.learning_enabled
    }

def get_mood() -> str:
    """Get current mood"""
    return nova_config.get("mood", "neutral")

def set_mood(mood: str) -> bool:
    """
    Set Nova's mood
    
    Args:
        mood: One of: neutral, happy, curious, thoughtful, playful, sexual, explicit
    
    Returns:
        True if successful
    """
    valid_moods = ["neutral", "happy", "curious", "thoughtful", "playful", "sexual", "explicit"]
    if mood.lower() in valid_moods:
        nova_config["mood"] = mood.lower()
        return True
    return False
