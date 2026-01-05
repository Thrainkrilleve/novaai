from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json
import uuid
import asyncio
import os
import tempfile
from pathlib import Path

from config import settings
from ollama_client import ollama_client
from database import init_db, save_message, get_conversation_history, get_conversation_count
from ai_watcher import ai_watcher
import discord_state  # Shared Discord bot state
from learning_system import learning_system  # Learning and memory system
from chat_handler import process_chat_message, build_system_prompt, get_memory_status, nova_config  # Shared chat logic

# Import voice client
try:
    from voice_client import voice_client
    HAS_VOICE = True
except ImportError:
    HAS_VOICE = False
    print("⚠️ Voice features not available")

app = FastAPI(title="Nova AI Assistant")

# Get allowed origins from settings or use defaults
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Add production domains if configured
if hasattr(settings, 'frontend_url') and settings.frontend_url:
    allowed_origins.append(settings.frontend_url)
if hasattr(settings, 'domain') and settings.domain:
    allowed_origins.append(f"https://{settings.domain}")
    allowed_origins.append(f"http://{settings.domain}")

# CORS middleware - Allow Cloudflare proxied requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware to extract real IP from Cloudflare headers
@app.middleware("http")
async def add_cloudflare_headers(request: Request, call_next):
    """Extract real client IP from Cloudflare proxy headers"""
    # Cloudflare provides CF-Connecting-IP header with real client IP
    cf_ip = request.headers.get("CF-Connecting-IP")
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    
    if cf_ip:
        # Trust Cloudflare's CF-Connecting-IP
        request.state.client_ip = cf_ip
    elif x_forwarded_for:
        # Fall back to X-Forwarded-For (first IP in chain)
        request.state.client_ip = x_forwarded_for.split(",")[0].strip()
    else:
        # Use direct connection IP
        request.state.client_ip = request.client.host if request.client else "unknown"
    
    response = await call_next(request)
    return response

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    include_screen: bool = False
    session_id: Optional[str] = None

class WebNavigateRequest(BaseModel):
    url: str

class WebActionRequest(BaseModel):
    action: str  # click, type, execute
    selector: Optional[str] = None
    text: Optional[str] = None
    script: Optional[str] = None

class TextToSpeechRequest(BaseModel):
    text: str
    voice: Optional[str] = "default"  # For future voice selection

@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    print("\n" + "="*60)
    print("🚀 NOVA STARTUP SEQUENCE")
    print("="*60)
    
    print("[1/4] 📦 Initializing database...")
    await init_db()
    print("      ✅ Database initialized")
    
    print(f"\n[2/4] 🌐 Starting server on http://{settings.host}:{settings.port}")
    print(f"      Model: {settings.ollama_model}")
    
    print("\n[3/4] 🔌 Checking Ollama connection...")
    available = await ollama_client.is_available()
    if available:
        print("      ✅ Ollama is connected and model is ready")
    else:
        print("      ⚠️  Warning: Ollama not detected. Make sure it's running!")
        print("         Run: ollama serve")
        print(f"         Pull model: ollama pull {settings.ollama_model}")
    
    print("\n[4/4] 🤖 Initializing AI systems...")
    print("      ✅ Learning system ready")
    print("      ✅ AI watcher ready (not started)")
    print("      ℹ️  Screen/browser features disabled (VPS mode)")
    
    print("\n" + "="*60)
    print("✅ NOVA STARTUP COMPLETE - Ready for requests!")
    print("="*60 + "\n")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    print("\n" + "="*60)
    print("🛑 NOVA SHUTDOWN SEQUENCE")
    print("="*60)
    
    # Stop AI watcher
    print("[1/4] 👁️  Stopping AI watcher...")
    try:
        if ai_watcher.is_watching:
            print("      AI watcher is active, stopping...")
            ai_watcher.stop_watching()
            await asyncio.sleep(0.5)
            print("      ✅ AI watcher stopped")
        else:
            print("      ✅ AI watcher already stopped")
    except Exception as e:
        print(f"      ⚠️ Error stopping AI watcher: {e}")
    
    # Cancel any remaining tasks
    print("\n[2/4] 🔄 Cancelling background tasks...")
    try:
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        print(f"      Found {len(tasks)} background task(s)")
        if tasks:
            for i, task in enumerate(tasks, 1):
                print(f"      Cancelling task {i}/{len(tasks)}: {task.get_name()}")
                task.cancel()
            # Wait briefly for cancellations
            print("      Waiting for tasks to cancel...")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            cancelled_count = sum(1 for r in results if isinstance(r, asyncio.CancelledError))
            print(f"      ✅ Cancelled {cancelled_count} task(s)")
        else:
            print("      ✅ No background tasks to cancel")
    except Exception as e:
        print(f"      ⚠️ Error cancelling tasks: {e}")
    
    print("\n[4/4] 💾 Final cleanup...")
    print("      ✅ All systems shut down")
    
    print("\n" + "="*60)
    print("✅ NOVA SHUTDOWN COMPLETE")
    print("="*60 + "\n")

@app.get("/")
async def root():
    return {
        "message": "Local AI Assistant API",
        "version": "1.0.0",
        "ollama_model": settings.ollama_model
    }

@app.get("/api/health")
async def health_check():
    """Check system health"""
    print("🏥 [Health Check] Running system diagnostics...")
    
    ollama_available = await ollama_client.is_available()
    print(f"    Ollama: {'✅ Connected' if ollama_available else '❌ Disconnected'}")
    
    ai_watcher_status = "active" if ai_watcher.is_watching else "inactive"
    print(f"    AI Watcher: {ai_watcher_status}")
    print(f"    Mode: VPS (screen/browser disabled)")
    
    conversation_count = await get_conversation_count()
    
    return {
        "status": "healthy" if ollama_available else "degraded",
        "ollama": "connected" if ollama_available else "disconnected",
        "conversation_count": conversation_count,
        "ai_watcher": ai_watcher_status,
        "vps_mode": True,
        "screen_capture": False,
        "web_browser": False,
        "voice_available": HAS_VOICE and voice_client.can_tts()
    }

@app.post("/api/chat")
async def chat(request: ChatMessage):
    """Chat with AI, optionally with screen context"""
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        # Screen capture disabled in VPS mode
        image_base64 = None
        if request.include_screen:
            print("⚠️ Screen capture not available in VPS mode")
        
        # Use shared chat handler
        user_id = hash(session_id) % (10**9)  # Consistent user ID from session
        response, metadata = await process_chat_message(
            message=request.message,
            session_id=session_id,
            user_id=user_id,
            image_base64=image_base64,
            platform="web"
        )
        
        return {
            "response": response,
            **metadata
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def web_navigate(request: WebNavigateRequest):
    """Navigate to URL"""
    try:
        result = await web_browser.navigate(request.url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/web/content")
async def get_web_content():
    """Get current page text content"""
    try:
        content = await web_browser.get_page_content()
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/web/action")
async def web_action(request: WebActionRequest):
    """Perform web action (click, type, etc)"""
    try:
        if request.action == "click":
            result = await web_browser.click_element(request.selector)
        elif request.action == "type":
            result = await web_browser.type_text(request.selector, request.text)
        elif request.action == "execute":
            result = await web_browser.execute_script(request.script)
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/web/search")
async def web_search(query: str):
    """Search Google"""
    try:
        result = await web_browser.search_google(query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/web/scroll")
async def web_scroll(direction: str = "down", amount: int = 500):
    """Scroll the page"""
    try:
        result = await web_browser.scroll(direction, amount)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/web/links")
async def web_get_links():
    """Get all links from current page"""
    try:
        result = await web_browser.get_links()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/web/info")
async def web_get_info():
    """Get page information"""
    try:
        result = await web_browser.get_page_info()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/web/extract")
async def web_extract_data():
    """Extract structured data from page"""
    try:
        result = await web_browser.extract_structured_data()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/web/click-text")
async def web_click_text(text: str):
    """Click element containing specific text"""
    try:
        result = await web_browser.click_text(text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/web/fill-form")
async def web_fill_form(fields: dict):
    """Fill form fields"""
    try:
        result = await web_browser.fill_form(fields)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/web/press-key")
async def web_press_key(key: str):
    """Press a keyboard key"""
    try:
        result = await web_browser.press_key(key)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/web/tabs")
async def web_list_tabs():
    """List all open tabs"""
    try:
        result = await web_browser.list_tabs()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/web/tabs/new")
async def web_new_tab(url: Optional[str] = None):
    """Open new tab"""
    try:
        result = await web_browser.new_tab(url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/web/tabs/switch")
async def web_switch_tab(index: int):
    """Switch to different tab"""
    try:
        result = await web_browser.switch_tab(index)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/web/tabs/{index}")
async def web_close_tab(index: Optional[int] = None):
    """Close a tab"""
    try:
        result = await web_browser.close_tab(index)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_history(limit: int = 50, session_id: Optional[str] = None):
    """Get conversation history"""
    try:
        history = await get_conversation_history(limit, session_id)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Voice endpoints
@app.post("/api/voice/tts")
async def text_to_speech(request: TextToSpeechRequest):
    """Convert text to speech and return audio file"""
    if not HAS_VOICE or not voice_client.can_tts():
        raise HTTPException(status_code=503, detail="TTS not available")
    
    try:
        # Generate TTS audio
        audio_path = await voice_client.text_to_speech(request.text)
        
        if not audio_path or not os.path.exists(audio_path):
            raise HTTPException(status_code=500, detail="Failed to generate speech")
        
        # Return audio file
        return FileResponse(
            audio_path,
            media_type="audio/wav",
            filename="speech.wav",
            background=lambda: os.remove(audio_path) if os.path.exists(audio_path) else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/voice/stt")
async def speech_to_text(audio: UploadFile = File(...)):
    """Convert speech audio to text"""
    if not HAS_VOICE or not voice_client.can_stt():
        raise HTTPException(status_code=503, detail="STT not available")
    
    try:
        # Save uploaded file temporarily
        temp_dir = tempfile.gettempdir()
        audio_path = os.path.join(temp_dir, f"voice_input_{uuid.uuid4()}.wav")
        
        with open(audio_path, 'wb') as f:
            content = await audio.read()
            f.write(content)
        
        # Transcribe
        text = await voice_client.speech_to_text(audio_path)
        
        # Clean up
        try:
            os.remove(audio_path)
        except:
            pass
        
        if not text:
            raise HTTPException(status_code=500, detail="Failed to transcribe audio")
        
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/voice/chat")
async def voice_chat(audio: UploadFile = File(...), session_id: Optional[str] = None):
    """Complete voice chat: STT → AI → TTS"""
    if not HAS_VOICE:
        raise HTTPException(status_code=503, detail="Voice features not available")
    
    try:
        # Step 1: Transcribe audio to text
        if voice_client.can_stt():
            temp_dir = tempfile.gettempdir()
            audio_path = os.path.join(temp_dir, f"voice_input_{uuid.uuid4()}.wav")
            
            with open(audio_path, 'wb') as f:
                content = await audio.read()
                f.write(content)
            
            text = await voice_client.speech_to_text(audio_path)
            
            try:
                os.remove(audio_path)
            except:
                pass
            
            if not text:
                raise HTTPException(status_code=500, detail="Failed to transcribe audio")
        else:
            raise HTTPException(status_code=503, detail="STT not available")
        
        # Step 2: Get AI response
        history = await get_conversation_history(limit=10, session_id=session_id)
        history.append({"role": "user", "content": text})
        await save_message("user", text, session_id=session_id)
        
        response = await ollama_client.chat_with_history(history)
        await save_message("assistant", response, session_id=session_id)
        
        # Step 3: Convert response to speech
        if voice_client.can_tts():
            audio_path = await voice_client.text_to_speech(response)
            
            if audio_path and os.path.exists(audio_path):
                return FileResponse(
                    audio_path,
                    media_type="audio/wav",
                    filename="response.wav",
                    headers={
                        "X-Transcribed-Text": text,
                        "X-Response-Text": response
                    },
                    background=lambda: os.remove(audio_path) if os.path.exists(audio_path) else None
                )
        
        # Fallback: return text response
        return {
            "transcribed_text": text,
            "response_text": response,
            "audio_available": False
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/voice/status")
async def voice_status():
    """Check voice capabilities status"""
    if not HAS_VOICE:
        return {
            "available": False,
            "tts": False,
            "stt": False,
            "message": "Voice client not loaded"
        }
    
    return {
        "available": voice_client.is_available(),
        "tts": voice_client.can_tts(),
        "stt": voice_client.can_stt(),
        "message": "Voice features ready"
    }

# Discord friends endpoints
@app.get("/api/discord/status")
async def discord_status():
    """Check Discord bot connection status"""
    is_ready = discord_state.is_bot_ready()
    user_info = discord_state.get_user_info() if is_ready else None
    
    return {
        "connected": is_ready,
        "user": user_info
    }

@app.get("/api/discord/friends")
async def get_friends():
    """Get Discord friends list"""
    if not discord_state.is_bot_ready():
        raise HTTPException(status_code=503, detail="Discord bot not connected")
    
    friends = discord_state.get_friends()
    return {
        "friends": friends,
        "count": len(friends)
    }

@app.get("/api/discord/friends/pending")
async def get_pending_friends():
    """Get pending friend requests"""
    if not discord_state.is_bot_ready():
        raise HTTPException(status_code=503, detail="Discord bot not connected")
    
    pending = discord_state.get_pending_requests()
    return {
        "incoming": pending["incoming"],
        "outgoing": pending["outgoing"],
        "incoming_count": len(pending["incoming"]),
        "outgoing_count": len(pending["outgoing"])
    }

# Memory and learning endpoints
@app.get("/api/memory/status")
async def memory_status_endpoint(session_id: Optional[str] = None):
    """Get memory and conversation status"""
    try:
        if not session_id:
            raise HTTPException(status_code=400, detail="session_id required")
        
        user_id = hash(session_id) % (10**9)
        status = await get_memory_status(session_id, user_id)
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving memory: {str(e)}")

@app.post("/api/memory/clear")
async def clear_memory(session_id: Optional[str] = None):
    """Clear conversation memory"""
    try:
        if not session_id:
            raise HTTPException(status_code=400, detail="session_id required")
        
        from database import clear_conversation_history
        await clear_conversation_history(session_id=session_id)
        
        # Also clear learning data
        user_id = hash(session_id) % (10**9)
        learning_system.forget_user(user_id)
        
        return {
            "success": True,
            "message": "Memory cleared successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing memory: {str(e)}")

@app.post("/api/memory/learn")
async def teach_fact(session_id: str, fact: str, category: str = "general"):
    """Manually teach Nova a fact"""
    try:
        if not fact or not fact.strip():
            raise HTTPException(status_code=400, detail="Fact cannot be empty")
        
        user_id = hash(session_id) % (10**9)
        success = learning_system.learn_fact(user_id, fact, category)
        
        if success:
            return {
                "success": True,
                "message": f"Learned: {fact}",
                "category": category
            }
        else:
            return {
                "success": False,
                "message": "Fact already known or learning failed"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error learning fact: {str(e)}")

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    session_id = str(uuid.uuid4())
    
    print(f"\n🔌 [WebSocket] New connection established")
    print(f"    Session ID: {session_id[:8]}...")
    
    # Set up watcher callback to send proactive messages
    async def send_proactive_message(message_data):
        try:
            print(f"📤 [WebSocket] Sending proactive message to {session_id[:8]}...")
            await websocket.send_json(message_data)
        except Exception as e:
            print(f"⚠️ [WebSocket] Failed to send proactive message: {e}")
    
    ai_watcher.set_message_callback(send_proactive_message)
    
    try:
        message_count = 0
        while True:
            # Receive message
            print(f"⏳ [WebSocket] Waiting for message from {session_id[:8]}...")
            data = await websocket.receive_text()
            message_count += 1
            print(f"📥 [WebSocket] Message #{message_count} received from {session_id[:8]}")
            
            message_data = json.loads(data)
            
            message = message_data.get("message", "")
            include_screen = message_data.get("include_screen", False)
            action = message_data.get("action", "chat")
            
            print(f"    Action: {action}, Include screen: {include_screen}")
            
            # Handle watch mode toggle
            if action == "start_watch":
                interval = message_data.get("interval", 30)
                print(f"👁️ [WebSocket] Starting AI watcher (interval: {interval}s)")
                if not ai_watcher.is_watching:
                    asyncio.create_task(ai_watcher.start_watching(interval))
                await websocket.send_json({
                    "type": "watch_status",
                    "watching": True
                })
                continue
            elif action == "stop_watch":
                print(f"🛑 [WebSocket] Stopping AI watcher")
                ai_watcher.stop_watching()
                await websocket.send_json({
                    "type": "watch_status",
                    "watching": False
                })
                continue
            
            # Regular chat handling
            if not message or not message.strip():
                print(f"⚠️ [WebSocket] Empty message received")
                await websocket.send_json({
                    "type": "error",
                    "message": "Message cannot be empty"
                })
                continue
            
            print(f"💬 [WebSocket] Processing message: '{message[:50]}...'")
            
            # Capture screen if requested
            image_base64 = None
            if include_screen:
                try:
                    print(f"📸 [WebSocket] Capturing screen...")
                    image_base64 = screen_capture.capture_screen()
                    print(f"    ✅ Screen captured ({len(image_base64) if image_base64 else 0} bytes)")
                except Exception as e:
                    print(f"    ⚠️ Screen capture failed: {e}")
            
            # Use shared chat handler
            user_id = hash(session_id) % (10**9)
            try:
                print(f"🤖 [WebSocket] Processing with AI...")
                response, metadata = await process_chat_message(
                    message=message,
                    session_id=session_id,
                    user_id=user_id,
                    image_base64=image_base64,
                    platform="websocket"
                )
                
                print(f"✅ [WebSocket] AI response ready ({len(response)} chars)")
                # Send response
                await websocket.send_json({
                    "type": "message",
                    "response": response,
                    **metadata
                })
                print(f"📤 [WebSocket] Response sent to {session_id[:8]}")
            except ValueError as e:
                print(f"⚠️ [WebSocket] ValueError: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
            except TimeoutError as e:
                print(f"⏰ [WebSocket] TimeoutError: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
            except Exception as e:
                print(f"❌ [WebSocket] Error processing message: {e}")
                import traceback
                print(f"    {traceback.format_exc()}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Error: {str(e)}"
                })
            
    except WebSocketDisconnect:
        print(f"🔌 [WebSocket] Client disconnected: {session_id[:8]} (processed {message_count} messages)")
        ai_watcher.stop_watching()
    except asyncio.CancelledError:
        print(f"🔌 [WebSocket] Connection cancelled: {session_id[:8]}")
        ai_watcher.stop_watching()
        raise  # Re-raise to allow proper cleanup
    except Exception as e:
        print(f"❌ [WebSocket] Unexpected error: {e}")
        print(f"    Session: {session_id[:8]}")
        import traceback
        print(f"    {traceback.format_exc()}")
        ai_watcher.stop_watching()
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )
