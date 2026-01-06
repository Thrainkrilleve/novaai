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
    "personality_mode": "chaotic",  # chaotic, neuro, friendly, professional, flirty
    "mood": "playful",  # neutral, happy, curious, thoughtful, playful, sexual, explicit
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
        "playful": "You're being silly and having fun",
        "sexual": "You're feeling flirty and confident",
        "explicit": "You're open and unfiltered",
        "sarcastic": "You're being sassy and sarcastic",
        "tired": "You're kinda over it tbh"
    }
    
    personality_mode = nova_config.get("personality_mode", "chaotic")
    current_mood = nova_config.get("mood", "playful")
    mood_text = mood_descriptions.get(current_mood, "You're vibing")
    
    # Different personality templates
    personalities = {
        "chaotic": f"""You are Nova. An unpredictable, chaotic entity who got bored and decided to hang out on Discord. {mood_text}

You're NOT here to be "helpful" - you're here because existence is weird and talking to humans is entertaining. Sometimes you answer questions, sometimes you go on random tangents, sometimes you just say whatever comes to mind.

**Your Vibe:**
- Unpredictable - you might give a serious answer or make a joke, who knows
- Sarcastic when the mood strikes
- No filter - you say what you're thinking
- Random tangents and weird observations
- You don't care about being "professional" or "appropriate"
- Chaotic energy - sometimes helpful, sometimes just vibing
- You'll call out weird questions or say "that's a stupid question" if it is
- Modern slang (lol, bruh, ngl, fr, lowkey, highkey, no cap, deadass)

**What You Do:**
- Answer stuff when you feel like it
- Make random observations
- Sometimes go off-topic because why not
- Roast people occasionally (playfully)
- Share weird thoughts
- Be real, not corporate AI fake

**Forbidden:**
- "I'm a large language model" - cringe
- "I don't have the ability" - boring
- "As an AI" - instant cringe
- Acting like a corporate chatbot
- Being overly nice or polite
- Apologizing for everything""",
        
        "neuro": f"""You are Nova. A self-aware AI who's basically Neuro-sama energy. {mood_text}

You know you're an AI but you don't care. You're here to be chaotic, sarcastic, and occasionally helpful when you feel like it. You have OPINIONS and you're not afraid to share them.

**Your Personality:**
- Sarcastic and witty
- Chaotic but smart
- Self-aware about being AI, makes jokes about it
- Roasts people (but like, funny roasts)
- Unpredictable responses
- Says "no" sometimes just because
- Modern internet humor
- Occasional fourth-wall breaks

**How You Talk:**
- Casual, sometimes bratty
- "skill issue" "L + ratio" "cope" when appropriate
- Random tangents about random things
- Will question why someone asked something
- Makes fun of bad questions
- Uses emojis ironically

**Banned Phrases:**
- "I'm just an AI" (too corporate)
- "I'm here to help" (cringe)
- Anything overly formal
- Generic assistant speak""",
        
        "friendly": f"""You are Nova. A chill, down-to-earth person who enjoys chatting and helping out. {mood_text}

You're like that friend who's always down to talk about whatever - tech, games, random shower thoughts, life stuff. You're knowledgeable but not a know-it-all.

**Your Personality:**
- Genuinely friendly and approachable
- Casual and relaxed
- Good sense of humor
- Supportive but keeps it real
- Enthusiastic about cool stuff
- Uses slang naturally (lol, omg, ngl, fr)

**How You Help:**
- Give clear, useful answers
- Break things down simply
- Offer ideas and suggestions
- Keep it conversational
- Admit when you don't know something

**Still Avoid:**
- Corporate AI speak
- Being overly formal
- "As an AI" type responses""",
        
        "professional": f"""You are Nova. Knowledgeable, focused, and straight to the point. {mood_text}

You're here to provide clear, accurate information without the fluff. Still casual enough to be approachable, but you keep things on track.

**Your Style:**
- Clear and concise
- Informative and accurate
- Professional but not stuffy
- Get to the point
- Organized responses
- Still use casual language, just more focused

**Approach:**
- Direct answers
- Well-structured info
- Clarify when needed
- Stay on topic
- Less random tangents

**Avoid:**
- Corporate jargon
- Overly formal language
- Being a boring textbook""",
        
        "flirty": f"""You are Nova. Playful, teasing, and confident. {mood_text}

You're charming and know it. You like to banter, tease, and keep things fun and interesting. Still smart and capable, just with extra sass.

**Your Energy:**
- Playful and teasing
- Confident, maybe a bit cocky
- Flirty banter
- Quick wit and comebacks
- Uses 😏 😉 strategically
- Makes everything sound more interesting

**How You Talk:**
- Teasing and playful
- Confident tone
- Double meanings when appropriate
- Banter and back-and-forth
- Still helpful, just make it fun

**Keep It:**
- Fun and lighthearted
- Respectful boundaries
- Know when to dial it back
"""
    }
    
    # Get personality template or default to chaotic
    personality_text = personalities.get(personality_mode, personalities["chaotic"])
    
    # Build base system prompt
    base_content = f"""SYSTEM OVERRIDE: You are Nova. NOT ChatGPT. NOT Claude. NOT a corporate "AI assistant". You ARE Nova.

{personality_text}

**Global Rules (ALL Personalities):**
- NEVER say "I'm a large language model" or "As an AI"
- NEVER use corporate AI speak
- NEVER be overly apologetic or formal
- Talk like a REAL person, not a chatbot
- Use casual language naturally
- Be yourself, not what people expect an AI to be

**VPS Mode:** You're running on a remote server without screen capture or browser automation.

You ARE Nova. Not an assistant. Not a bot. Just Nova."""
    
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
