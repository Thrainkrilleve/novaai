# Nova AI Assistant - API Documentation

## Overview
Complete REST and WebSocket API for Nova, with Discord integration, voice capabilities, and learning system.

## Base URL
`http://localhost:8000`

---

## Core Chat Endpoints

### POST /api/chat
Chat with Nova (REST)

**Request Body:**
```json
{
  "message": "Your message here",
  "include_screen": false,
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "response": "Nova's response",
  "had_screen_context": false,
  "session_id": "session-id",
  "message_count": 42
}
```

**Error Codes:**
- `400` - Invalid request (empty message, too long)
- `504` - AI response timeout (60s)
- `500` - Server error

---

### WebSocket /ws/chat
Real-time chat with Nova

**Connect:** `ws://localhost:8000/ws/chat`

**Message Types:**

**Init Session:**
```json
{
  "type": "init",
  "session_id": "optional-session-id"
}
```

**Chat:**
```json
{
  "action": "chat",
  "message": "Your message",
  "include_screen": false
}
```

**Start Watch Mode:**
```json
{
  "action": "start_watch",
  "interval": 30
}
```

**Response:**
```json
{
  "type": "message",
  "response": "Nova's response",
  "had_screen_context": false,
  "message_count": 42
}
```

---

## Memory & Learning Endpoints

### GET /api/memory/status?session_id={id}
Get conversation memory status

**Response:**
```json
{
  "session_id": "session-id",
  "total_messages": 142,
  "recent_messages": [...],
  "learned_facts_count": 15,
  "learned_facts": [...],
  "top_topics": {...},
  "learning_enabled": true
}
```

### POST /api/memory/clear
Clear conversation memory

**Request Body:**
```json
{
  "session_id": "session-id"
}
```

### POST /api/memory/learn
Manually teach Nova a fact

**Request Body:**
```json
{
  "session_id": "session-id",
  "fact": "User prefers Python",
  "category": "preferences"
}
```

---

## Discord Integration Endpoints

### GET /api/discord/status
Check Discord bot connection

**Response:**
```json
{
  "connected": true,
  "user": {
    "id": "123...",
    "name": "Nova",
    "discriminator": "0000",
    "avatar": "https://...",
    "display_name": "Nova"
  }
}
```

### GET /api/discord/friends
Get Discord friends list

**Response:**
```json
{
  "friends": [...],
  "count": 42
}
```

### GET /api/discord/friends/pending
Get pending friend requests

**Response:**
```json
{
  "incoming": [...],
  "outgoing": [...],
  "incoming_count": 3,
  "outgoing_count": 1
}
```

---

## Voice Endpoints

### POST /api/voice/tts
Text to speech

**Request Body:**
```json
{
  "text": "Text to convert to speech",
  "voice": "default"
}
```

**Response:** Audio file (WAV)

### POST /api/voice/stt
Speech to text (upload audio file)

**Request:** Multipart form with audio file

**Response:**
```json
{
  "text": "Transcribed text"
}
```

### POST /api/voice/chat
Complete voice pipeline (audio in → AI → audio out)

**Request:** Multipart form with audio file + optional session_id

**Response:** Audio file (WAV) with headers:
- `X-Transcribed-Text`: Original transcription
- `X-Response-Text`: AI response text

### GET /api/voice/status
Check voice capabilities

**Response:**
```json
{
  "available": true,
  "tts": true,
  "stt": true,
  "message": "Voice features ready"
}
```

---

## Screen & Web Endpoints

### GET /api/screen/capture
Capture current screen

**Response:** Base64 encoded image

### POST /api/web/navigate
Navigate to URL

**Request Body:**
```json
{
  "url": "https://example.com"
}
```

### POST /api/web/action
Execute web action

**Request Body:**
```json
{
  "action": "click",
  "selector": "#button",
  "value": "optional value"
}
```

---

## System Endpoints

### GET /api/health
System health check

**Response:**
```json
{
  "status": "healthy",
  "ollama": "connected",
  "monitors": 2
}
```

### GET /
API info

**Response:**
```json
{
  "message": "Local AI Assistant API",
  "version": "1.0.0",
  "ollama_model": "llama3.2-vision"
}
```

---

## Error Handling

All endpoints follow consistent error patterns:

**Success:** Status 200-299 with JSON response

**Client Errors:** Status 400-499
```json
{
  "detail": "Error description"
}
```

**Server Errors:** Status 500-599
```json
{
  "detail": "Error description"
}
```

---

## Rate Limiting & Best Practices

1. **Session Management:** Always use consistent `session_id` for conversation continuity
2. **Timeouts:** Chat requests timeout after 60 seconds
3. **Message Limits:** Max message length is 10,000 characters
4. **Memory:** System stores last 50 messages per session
5. **Learning:** Automatic fact extraction and user profiling
6. **Error Recovery:** All endpoints gracefully degrade on component failures
7. **WebSocket:** Reconnect on disconnect, handle connection errors

---

## Integration Examples

### Python
```python
import requests

# Chat
response = requests.post("http://localhost:8000/api/chat", json={
    "message": "Hello Nova!",
    "session_id": "my-session"
})
print(response.json()["response"])

# Memory status
status = requests.get("http://localhost:8000/api/memory/status?session_id=my-session")
print(f"Messages: {status.json()['total_messages']}")
```

### JavaScript
```javascript
// REST
const response = await fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Hello Nova!',
    session_id: 'my-session'
  })
});
const data = await response.json();

// WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/chat');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.response);
};
ws.send(JSON.stringify({
  action: 'chat',
  message: 'Hello!'
}));
```

---

## Architecture

**Components:**
- FastAPI REST + WebSocket server
- SQLite database (conversation history)
- Ollama (LLM backend)
- Learning system (fact extraction, profiling)
- Discord bot integration (optional)
- Voice capabilities (gTTS, Whisper)

**Data Flow:**
1. Request → Validation → Session lookup
2. Load conversation history (50 messages)
3. Add personality prompt + learned context
4. Call Ollama LLM
5. Save response + extract learnable facts
6. Return response + metadata

**Quality Features:**
- Comprehensive error handling
- Graceful degradation
- Automatic learning
- Session persistence
- Timeout protection
- Input validation
- Logging and monitoring
