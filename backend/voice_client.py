"""
Voice capabilities for Nova - TTS and STT
"""

import asyncio
import io
import os
import sys
import tempfile
import wave
from pathlib import Path

# Fix console encoding for Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False
    print("⚠️ pyttsx3 not available - basic TTS disabled")

try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False
    print("⚠️ gTTS not available - Google TTS disabled")

try:
    import whisper
    HAS_WHISPER = True
    print("✅ OpenAI Whisper loaded for STT")
except ImportError:
    HAS_WHISPER = False
    print("⚠️ OpenAI Whisper not available - STT disabled")

try:
    import discord
    HAS_VOICE = hasattr(discord, 'FFmpegPCMAudio')
except:
    HAS_VOICE = False
    print("⚠️ Discord voice features not available")

class VoiceClient:
    """Handles voice channel operations, TTS, and STT"""
    
    def __init__(self):
        self.tts_engine = None
        self.whisper_model = None
        self.voice_clients = {}  # channel_id -> voice_client
        self.listening_tasks = {}  # channel_id -> task
        self.tts_lock = asyncio.Lock()  # Prevent concurrent TTS operations
        self.audio_buffers = {}  # channel_id -> {user_id: audio_buffer}
        self.voice_callback = None  # Callback for when voice is detected
        
        # Initialize TTS
        if HAS_PYTTSX3:
            try:
                self.tts_engine = pyttsx3.init()
                # Configure voice settings
                voices = self.tts_engine.getProperty('voices')
                # Try to use a female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                self.tts_engine.setProperty('rate', 175)  # Speed
                self.tts_engine.setProperty('volume', 0.9)  # Volume
                print("✅ TTS engine initialized")
            except Exception as e:
                print(f"❌ Failed to initialize TTS: {e}")
                self.tts_engine = None
        
        # Initialize Whisper for STT
        if HAS_WHISPER:
            try:
                print("⏳ Loading Whisper model (first time may take a while)...")
                # Use base model for speed (can change to small, medium, large)
                self.whisper_model = whisper.load_model("base")
                print("✅ Whisper STT model loaded (base)")
            except Exception as e:
                print(f"❌ Failed to load Whisper: {e}")
                self.whisper_model = None
    
    def is_available(self):
        """Check if voice features are available"""
        return HAS_VOICE and (HAS_PYTTSX3 or HAS_WHISPER)
    
    def can_tts(self):
        """Check if TTS is available"""
        return HAS_GTTS or HAS_PYTTSX3
    
    def can_stt(self):
        """Check if STT is available"""
        return self.whisper_model is not None
    
    async def text_to_speech(self, text: str) -> str:
        """
        Convert text to speech and save as audio file
        Returns path to audio file
        """
        if not self.can_tts():
            return None
        
        # Use lock to prevent concurrent TTS operations (pyttsx3 is not thread-safe)
        async with self.tts_lock:
            try:
                # Create temp file for audio
                temp_dir = tempfile.gettempdir()
                audio_path = os.path.join(temp_dir, f"nova_tts_{os.getpid()}.wav")
                
                print(f"🔒 TTS lock acquired, generating audio...")
                
                # Run TTS in executor to avoid blocking
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self._tts_save, text, audio_path)
                
                print(f"✅ TTS generation complete, releasing lock")
                
                return audio_path
            except Exception as e:
                print(f"❌ TTS error: {e}")
                return None
    
    def _tts_save(self, text: str, path: str):
        """Internal: Save TTS to file (blocking) - uses gTTS (more reliable than pyttsx3)"""
        try:
            # Use gTTS if available (more reliable for multiple calls)
            if HAS_GTTS:
                tts = gTTS(text=text, lang='en', slow=False)
                tts.save(path)
                print(f"✅ gTTS generated audio successfully")
            elif HAS_PYTTSX3:
                # Fallback to pyttsx3 (has issues with multiple calls)
                engine = pyttsx3.init()
                voices = engine.getProperty('voices')
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
                engine.setProperty('rate', 175)
                engine.setProperty('volume', 0.9)
                engine.save_to_file(text, path)
                engine.runAndWait()
                del engine
                print(f"✅ pyttsx3 generated audio successfully")
            else:
                raise Exception("No TTS engine available")
            
        except Exception as e:
            print(f"❌ _tts_save error: {e}")
            raise
    
    async def speech_to_text(self, audio_path: str) -> str:
        """
        Convert audio file to text using Whisper
        Returns transcribed text
        """
        if not self.can_stt():
            return None
        
        try:
            # Run Whisper in executor to avoid blocking
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(None, self._whisper_transcribe, audio_path)
            return text
        except Exception as e:
            print(f"❌ STT error: {e}")
            return None
    
    def _whisper_transcribe(self, audio_path: str) -> str:
        """Internal: Transcribe audio (blocking)"""
        result = self.whisper_model.transcribe(audio_path, fp16=False)
        return result["text"].strip()
    
    async def join_voice_channel(self, channel):
        """Join a voice channel"""
        if not HAS_VOICE:
            return None, "Voice features not available (discord.py-self may not support voice)"
        
        try:
            # First, disconnect if already connected to this channel
            if channel.id in self.voice_clients:
                try:
                    await self.voice_clients[channel.id].disconnect()
                    await asyncio.sleep(0.5)  # Give Discord time to process disconnect
                except:
                    pass
                del self.voice_clients[channel.id]
            
            # Connect to the channel
            voice_client = await channel.connect(timeout=10.0, reconnect=False)
            self.voice_clients[channel.id] = voice_client
            return voice_client, None
        except asyncio.TimeoutError:
            return None, "Connection timeout - Discord voice servers may be slow"
        except Exception as e:
            return None, f"Failed to join voice channel: {e}"
    
    async def leave_voice_channel(self, channel_id: int):
        """Leave a voice channel"""
        if channel_id in self.voice_clients:
            try:
                await self.voice_clients[channel_id].disconnect()
                del self.voice_clients[channel_id]
                
                # Stop listening task if active
                if channel_id in self.listening_tasks:
                    self.listening_tasks[channel_id].cancel()
                    del self.listening_tasks[channel_id]
                
                return True
            except Exception as e:
                print(f"❌ Error leaving voice: {e}")
                return False
        return False
    
    async def speak_in_channel(self, channel_id: int, text: str):
        """
        Speak text in a voice channel
        """
        print(f"🎤 speak_in_channel called - channel: {channel_id}, text: '{text[:30]}...'")
        
        if channel_id not in self.voice_clients:
            print(f"❌ Voice speak error: Not in voice channel {channel_id}")
            print(f"   Available channels: {list(self.voice_clients.keys())}")
            return False, "Not in voice channel"
        
        if not self.can_tts():
            print(f"❌ Voice speak error: TTS not available")
            return False, "TTS not available"
        
        voice_client = self.voice_clients[channel_id]
        print(f"✅ Got voice client: {voice_client}")
        
        try:
            print(f"🔊 Generating TTS audio for: '{text[:50]}...'")
            # Generate audio
            audio_path = await self.text_to_speech(text)
            print(f"🔄 After TTS generation, audio_path: {audio_path}")
            if not audio_path:
                print(f"❌ Failed to generate TTS audio file")
                return False, "Failed to generate speech"
            
            print(f"✅ TTS audio generated: {audio_path}")
            print(f"   File exists: {os.path.exists(audio_path)}")
            if os.path.exists(audio_path):
                print(f"   File size: {os.path.getsize(audio_path)} bytes")
            
            # Play audio
            if voice_client.is_playing():
                print(f"⏹️ Stopping current playback")
                voice_client.stop()
                # Wait for playback to actually stop
                for i in range(20):  # Wait up to 2 seconds
                    await asyncio.sleep(0.1)
                    if not voice_client.is_playing():
                        break
                else:
                    print(f"⚠️ Timeout waiting for playback to stop")
            
            print(f"▶️ Creating FFmpeg audio source...")
            try:
                audio_source = discord.FFmpegPCMAudio(audio_path)
                print(f"✅ FFmpeg audio source created")
            except Exception as ffmpeg_error:
                print(f"❌ FFmpeg error: {ffmpeg_error}")
                import traceback
                traceback.print_exc()
                return False, f"FFmpeg error: {ffmpeg_error}"
            
            print(f"🎵 Starting playback in Discord voice channel...")
            voice_client.play(audio_source, after=lambda e: self._cleanup_audio(audio_path, e))
            
            print(f"✅ Audio playback started successfully")
            return True, None
        except Exception as e:
            print(f"❌ Voice speak exception: {e}")
            import traceback
            traceback.print_exc()
            traceback.print_exc()
            return False, f"Failed to speak: {e}"
    
    def _cleanup_audio(self, path: str, error):
        """Clean up temp audio file after playing"""
        try:
            if os.path.exists(path):
                os.remove(path)
        except:
            pass
        
        if error:
            print(f"❌ Playback error: {error}")
    
    def get_voice_client(self, channel_id: int):
        """Get voice client for a channel"""
        return self.voice_clients.get(channel_id)
    
    def is_connected(self, channel_id: int) -> bool:
        """Check if connected to a voice channel"""
        return channel_id in self.voice_clients
    
    async def disconnect_all(self):
        """Disconnect from all voice channels (cleanup on shutdown/restart)"""
        for channel_id in list(self.voice_clients.keys()):
            try:
                await self.leave_voice_channel(channel_id)
                print(f"✅ Disconnected from voice channel {channel_id}")
            except Exception as e:
                print(f"⚠️ Error disconnecting from {channel_id}: {e}")
    
    def set_voice_callback(self, callback):
        """Set callback function for voice detection (callback receives channel, user, text)"""
        self.voice_callback = callback
    
    async def start_listening(self, channel_id: int):
        """Start listening to voice in a channel (Discord.py-self has limited support)"""
        if channel_id not in self.voice_clients:
            return False, "Not in voice channel"
        
        if not self.can_stt():
            return False, "STT not available"
        
        voice_client = self.voice_clients[channel_id]
        
        # Note: Discord.py-self has very limited voice receiving support
        # This is a placeholder for when/if it becomes available
        print(f"⚠️ Voice listening started on channel {channel_id}")
        print(f"⚠️ Note: Discord.py-self has limited voice receiving capabilities")
        print(f"💡 Consider using a voice activity detection webhook or manual transcription")
        
        return True, None

# Global instance
voice_client = VoiceClient()
