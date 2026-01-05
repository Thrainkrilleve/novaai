import asyncio
from typing import Callable, Optional
from datetime import datetime
import time
import hashlib

from screen_capture import screen_capture
from ollama_client import ollama_client
from database import save_message
from web_browser import web_browser

class AIWatcher:
    """Proactive AI that monitors screen and initiates conversations"""
    
    def __init__(self):
        self.is_watching = False
        self.watch_interval = 30  # seconds between checks
        self.last_screenshot_time = 0
        self.last_context = ""
        self.last_screen_hash = None
        self.on_message_callback: Optional[Callable] = None
        self.session_id = "watcher"
        
    def set_message_callback(self, callback: Callable):
        """Set callback for when AI wants to say something"""
        self.on_message_callback = callback
        
    async def start_watching(self, interval: int = 30):
        """Start proactive monitoring"""
        self.is_watching = True
        self.watch_interval = interval
        
        print(f"\n👁️  [AI Watcher] Starting monitoring (interval: {interval}s)")
        print(f"    Session ID: {self.session_id}")
        
        iteration = 0
        try:
            while self.is_watching:
                try:
                    iteration += 1
                    print(f"👁️  [AI Watcher] Iteration {iteration} - Sleeping for {self.watch_interval}s...")
                    await asyncio.sleep(self.watch_interval)
                    
                    if self.is_watching:
                        print(f"👁️  [AI Watcher] Iteration {iteration} - Checking screen...")
                        await self._check_screen()
                        print(f"👁️  [AI Watcher] Iteration {iteration} - Screen check complete")
                except asyncio.CancelledError:
                    print(f"👁️  [AI Watcher] Received cancellation request at iteration {iteration}")
                    break
                except Exception as e:
                    print(f"⚠️  [AI Watcher] Error at iteration {iteration}: {e}")
                    import traceback
                    print(f"    {traceback.format_exc()}")
        finally:
            self.is_watching = False
            print(f"👁️  [AI Watcher] Monitoring stopped after {iteration} iterations")
    
    def stop_watching(self):
        """Stop monitoring"""
        self.is_watching = False
        print("👁️ AI Watcher stopped")
    
    async def _check_screen(self):
        """Check screen and potentially initiate conversation"""
        try:
            # Capture screen
            image_base64 = screen_capture.capture_screen()
            
            if not image_base64:
                return
            
            # Check if screen has changed significantly
            screen_hash = hashlib.md5(image_base64.encode()).hexdigest()
            
            if screen_hash == self.last_screen_hash:
                print(f"🤖 Screen unchanged, skipping analysis")
                return
            
            self.last_screen_hash = screen_hash
            
            # Create monitoring prompt
            current_time = datetime.now().strftime("%I:%M %p")
            
            prompt = f"""You are an AI assistant with vision capabilities viewing the user's screen at {current_time}.

IMPORTANT: You are looking at a screenshot image right now. Describe what you see.

Previous context: {self.last_context if self.last_context else "This is your first observation."}

YOU HAVE WEB BROWSING CAPABILITIES. You can autonomously:
- Search Google for information
- Visit websites to gather data
- Read documentation or articles

Analyze what you see on the screen right now and THINK OUT LOUD about your observations:

STEP 1 - OBSERVE: What do you see? What's the user doing?
STEP 2 - ANALYZE: What's interesting, concerning, or noteworthy?
STEP 3 - REASON: Should you help? Why or why not?
STEP 4 - DECIDE: What action makes the most sense?

When responding, SHOW YOUR REASONING by explaining:
- What you notice on the screen
- Why it caught your attention
- What you're thinking about doing
- Your decision and rationale

Examples of good responses:
- "I notice you're getting a Python import error on line 45. This usually means the module isn't installed. Would you like me to search for the solution?"
- "I see you're reading documentation about async functions. I'm observing this because you were just writing async code. Let me know if you need clarification on anything!"
- "You're on a GitHub repository page for a web scraping library. I'm paying attention since you mentioned wanting to build a scraper earlier. Should I look into this library's documentation?"

IMPORTANT RULES:
- SHOW YOUR THINKING - explain what you see and why it matters
- Be thoughtful and analytical, not just observational
- Only speak if you have genuine insight or assistance to offer
- Don't repeat yourself if nothing meaningful has changed
- Be proactive but not intrusive

TO BROWSE THE WEB, respond with:
SEARCH: <query> - to search Google
VISIT: <url> - to visit a specific website
ANALYZE_PAGE - to analyze the current webpage

If you want to browse, respond ONLY with the command.
If you have nothing to say, respond with exactly: "SILENT"
Otherwise, share your observations and reasoning.

What do you observe and think?"""

            # Get AI response
            response = await ollama_client.chat(prompt, image_base64)
            
            response = response.strip()
            
            # Check for web browsing commands
            if response.startswith("SEARCH:"):
                query = response.replace("SEARCH:", "").strip()
                await self._handle_search(query)
                return
            elif response.startswith("VISIT:"):
                url = response.replace("VISIT:", "").strip()
                await self._handle_visit(url)
                return
            elif response.upper() == "ANALYZE_PAGE":
                await self._handle_analyze_page()
                return
            
            # Check if AI wants to say something
            if response and response.upper() != "SILENT":
                # Update context
                self.last_context = f"I said: {response}"
                
                # Send message via callback
                if self.on_message_callback:
                    await self.on_message_callback({
                        "type": "proactive",
                        "content": response,
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Save to database
                await save_message("assistant", response, session_id=self.session_id)
                
                print(f"🤖 AI spoke: {response}")
            else:
                print(f"🤖 AI monitoring... (staying silent)")
                
        except Exception as e:
            print(f"Error in watcher: {e}")
    
    async def _handle_search(self, query: str):
        """Handle autonomous web search"""
        try:
            print(f"🔍 AI is searching: {query}")
            result = await web_browser.search_google(query)
            
            if result.get('success'):
                results_text = f"Found {len(result.get('results', []))} results for: {query}"
                
                # Notify user
                if self.on_message_callback:
                    await self.on_message_callback({
                        "type": "proactive",
                        "content": f"🔍 I searched Google for '{query}' and found some relevant information.",
                        "timestamp": datetime.now().isoformat()
                    })
                
                self.last_context = f"I searched for: {query}"
            
        except Exception as e:
            print(f"Search error: {e}")
    
    async def _handle_visit(self, url: str):
        """Handle autonomous website visit"""
        try:
            print(f"🌐 AI is visiting: {url}")
            result = await web_browser.navigate(url)
            
            if result.get('success'):
                # Get page summary
                content = await web_browser.get_page_content()
                summary = content[:500] if content else "No content"
                
                # Notify user
                if self.on_message_callback:
                    await self.on_message_callback({
                        "type": "proactive",
                        "content": f"🌐 I visited {result.get('title', url)} to gather more information.",
                        "timestamp": datetime.now().isoformat()
                    })
                
                self.last_context = f"I visited: {url}"
                
        except Exception as e:
            print(f"Visit error: {e}")
    
    async def _handle_analyze_page(self):
        """Analyze current webpage"""
        try:
            content = await web_browser.get_page_content()
            
            if content and not content.startswith("Error"):
                # Ask AI to analyze
                analysis = await ollama_client.chat(
                    f"Briefly summarize this webpage in 1-2 sentences:\n\n{content[:2000]}"
                )
                
                if self.on_message_callback:
                    await self.on_message_callback({
                        "type": "proactive",
                        "content": f"📄 {analysis}",
                        "timestamp": datetime.now().isoformat()
                    })
                    
        except Exception as e:
            print(f"Analyze error: {e}")
    
    async def enable_smart_alerts(self):
        """Enable alerts for specific events"""
        # This could be extended to detect specific patterns
        pass

# Global instance
ai_watcher = AIWatcher()
