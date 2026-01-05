# 🧠 Nova Learning System

Nova now has a sophisticated learning and memory system! She can remember facts about you, track your interests, and adapt her responses based on what she learns.

## Features

### 📝 Fact Learning
- **Automatic**: Nova automatically detects and learns facts from your conversations
- **Manual**: You can explicitly teach Nova facts about yourself
- **Categories**: Facts are organized by type (name, location, preferences, etc.)
- **Persistent**: All learned information is saved to disk

### 🎯 Interest Tracking
- Nova tracks topics you talk about frequently
- Weight system shows which topics you're most interested in
- Helps Nova understand your preferences and priorities

### 📊 Interaction Statistics
- Tracks total messages exchanged
- Records first interaction date
- Monitors conversation patterns
- Helps Nova build a relationship history with you

### 🤖 Adaptive Responses
- Nova uses learned information in conversations
- Adds context to her system prompt based on what she knows
- Personalizes responses based on your preferences

## Commands

### `!learn show`
View what Nova knows about you:
- Facts learned (recent)
- Topics of interest with weights
- Statistics summary

```
!learn show
```

### `!learn tell <fact>`
Explicitly teach Nova something about you:
```
!learn tell I love playing EVE Online
!learn tell My favorite color is blue
!learn tell I'm a software developer
```

### `!learn topics`
See all topics you've discussed with weighted bars:
```
!learn topics
```

### `!learn forget`
Erase all of Nova's memory about you (fresh start):
```
!learn forget
```

### `!profile`
View your complete learning profile with formatted embed:
```
!profile
```

## Automatic Learning

Nova automatically learns from natural conversation:

**Name Recognition:**
- "my name is John"
- "call me Mike"
- "I'm called Sarah"

**Location:**
- "I live in New York"
- "I'm from California"

**Occupation:**
- "I work as a developer"
- "I'm a teacher"

**Preferences:**
- "my favorite game is EVE"
- "I love pizza"
- "I hate cold weather"

**Possessions:**
- "I have a cat"
- "I own a Tesla"

**Example Conversation:**
```
You: My name is Alex and I love programming
Nova: *learns: "Alex" (name), "love programming" (preference)*

You: I'm from Seattle and work as a software engineer
Nova: *learns: "from Seattle" (location), "work as a software engineer" (occupation)*
```

## Data Storage

Learning data is stored in `backend/data/` directory:
- `user_<id>.json` - One file per user
- Contains: profile, facts, preferences, stats, topics
- Auto-saves periodically
- JSON format for easy backup/inspection

### Data Structure:
```json
{
  "profile": {
    "name": "Alex"
  },
  "facts": [
    {
      "fact": "loves programming",
      "category": "preference",
      "learned_at": "2026-01-03T...",
      "confidence": 1.0
    }
  ],
  "preferences": {
    "favorite_game": "EVE Online"
  },
  "stats": {
    "total_messages": 150,
    "first_interaction": "2026-01-01T...",
    "last_interaction": "2026-01-03T..."
  },
  "topics": {
    "eve online": 8.5,
    "programming": 7.2,
    "python": 5.1
  }
}
```

## Privacy & Control

### Disable Learning Globally
```
!learn disable
```

### Enable Learning
```
!learn enable
```

### Clear Your Data
```
!learn forget
```

### Manual Data Deletion
Delete your file: `backend/data/user_<your_discord_id>.json`

## Technical Details

### Learning Limits
- **Max Facts per User:** 100 (oldest removed when exceeded)
- **Max Topics per User:** 50 (lowest weighted removed)
- **Confidence System:** Facts have confidence scores (future feature)
- **Category System:** Facts organized by type for better retrieval

### Integration Points

1. **Chat Handler** ([discord_bot.py](backend/discord_bot.py) line ~1680)
   - Injects learned context into system prompt
   - Automatically extracts learnable info from messages
   - Tracks interactions

2. **System Prompt Enhancement**
   - Adds "What You Know About This User" section
   - Includes facts, preferences, topics
   - Helps Nova provide personalized responses

3. **Auto-Save**
   - Saves after every fact learned
   - Saves every 10 messages for stats
   - Prevents data loss

## Use Cases

### Personal Assistant
```
You: My doctor appointment is on Friday
Nova: *learns: appointment Friday*
[Later]
You: What do I have this week?
Nova: You mentioned your doctor appointment on Friday!
```

### Preference Memory
```
You: I prefer Python over JavaScript
Nova: *learns preference*
[Later]
Nova: *suggests Python solutions instead of JavaScript*
```

### Topic Expertise
```
You: *talks about EVE Online frequently*
Nova: *weights "eve online" topic heavily*
Nova: *becomes more knowledgeable and engaging about EVE*
```

### Relationship Building
```
You: *chats over weeks*
Nova: *tracks 500+ messages*
Nova: We've been talking for 3 weeks! You're really into [top topics]
```

## Future Enhancements

### Planned Features:
- 🎭 **Personality Adaptation** - Nova's personality evolves based on your interactions
- 🔮 **Predictive Learning** - Anticipate what you'll want to know
- 📅 **Event Memory** - Remember important dates, appointments
- 🤝 **Relationship Context** - Track relationships between users
- 🧩 **Fact Linking** - Connect related facts for deeper understanding
- 📊 **Learning Analytics** - Visualize learning graphs and patterns
- 🔐 **Encrypted Storage** - Option for encrypted user data
- 🌐 **Cross-Channel Learning** - Learn across different Discord servers
- 💬 **Conversation Summarization** - Generate summaries of past conversations
- 🎯 **Goal Tracking** - Help users achieve their goals by remembering them

### Advanced Ideas:
- RAG (Retrieval Augmented Generation) with vector database
- Fine-tuning based on user conversations
- Sentiment analysis for mood tracking
- Multi-user conversation understanding
- Export/import learning profiles

## Troubleshooting

### Nova Isn't Learning
1. Check if learning is enabled: `!learn show`
2. If disabled, enable it: `!learn enable`
3. Try explicitly teaching: `!learn tell <fact>`

### Facts Not Saving
1. Check `backend/data/` directory exists
2. Verify write permissions
3. Check console for errors

### Too Much/Wrong Information
1. Use `!learn forget` to reset
2. Learning will restart from scratch
3. Be more explicit in teaching facts

### Want to Transfer Learning Data
1. Copy your `user_<id>.json` file
2. Move to new installation's `backend/data/` folder
3. Nova will load it automatically

## Examples

### Getting Started
```
You: !learn show
Nova: No facts learned yet

You: !learn tell I'm a game developer who loves sci-fi
Nova: ✅ Got it! I'll remember: I'm a game developer who loves sci-fi

You: !learn show
Nova: 📊 Learning Profile
      Facts Learned: 1
      Recent Facts:
      • I'm a game developer who loves sci-fi
```

### Natural Learning
```
You: Hey Nova, my name is Marcus and I live in London
Nova: *learns automatically*
      🧠 Learned: name - Marcus
      🧠 Learned: location - London

You: !profile
Nova: [Shows full profile with Marcus, London, and other data]
```

### Topic Tracking
```
You: *discusses Python coding multiple times*
Nova: *tracks "python" topic*

You: !learn topics
Nova: 📚 Your Topics of Interest:
      1. **python** ████████ (8.5)
      2. **coding** ██████ (6.2)
      3. **discord** ████ (4.1)
```

## Notes

- Learning is **opt-in by default** (automatically enabled)
- All data stays **local** on your machine
- No cloud sync or external services
- **Delete anytime** with `!learn forget`
- Works across **all channels** where you use Nova
- Learning data **enhances** but doesn't replace conversation history

---

**Nova's learning system makes her more personal, context-aware, and helpful over time!** 🧠✨
