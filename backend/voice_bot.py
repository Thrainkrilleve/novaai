"""
Nova Voice Bot - Handles voice listening and speaking
Runs alongside the main userbot to provide voice interaction
"""

import asyncio
import os
import tempfile
import discord
from discord.ext import commands
from dotenv import load_dotenv
import whisper
from gtts import gTTS
import aiohttp

# Load environment
load_dotenv()

# Add FFmpeg to PATH
ffmpeg_path = r"C:\ffmpeg\ffmpeg-8.0.1-essentials_build\bin"
if os.path.exists(ffmpeg_path):
    os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ.get("PATH", "")
    print(f"✅ FFmpeg path added: {ffmpeg_path}")
else:
    print("⚠️ FFmpeg not found at expected location")

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)  # Use same prefix as main bot

# Load Whisper model
print("⏳ Loading Whisper model...")
whisper_model = whisper.load_model("base")
print("✅ Whisper model loaded")

# Voice listening state
listening_channels = set()  # Set of channel IDs we're actively listening to
auto_respond = True  # Automatically respond to voice messages

# Ollama configuration
OLLAMA_URL = "http://localhost:11434"


# NOTE: Discord's API has VERY limited voice receiving support
# Voice-to-voice requires complex workarounds or external audio capture
# Current setup: Text messages → Voice responses (works great!)
# Future: Explore external audio recording tools for true voice input


class VoiceReceiver(discord.VoiceClient):
    """Custom voice client that can receive audio"""
    
    def __init__(self, client, channel):
        super().__init__(client, channel)
        self.audio_buffer = {}  # user_id -> audio_data
        self.callback = None
    
    async def on_voice_receive(self, user, data):
        """Called when voice data is received"""
        if self.callback:
            await self.callback(user, data)


@bot.event
async def on_ready():
    print(f'🎙️ Nova Voice Bot is online!')
    print(f'📊 Connected to {len(bot.guilds)} servers')
    print(f'🤖 Bot user: {bot.user.name}')


@bot.event
async def on_voice_state_update(member, before, after):
    """Monitor voice channel activity"""
    # If someone joins a channel we're listening to
    if after.channel and after.channel.id in listening_channels:
        print(f"👤 {member.name} joined voice channel")


@bot.command(name='join', aliases=['vjoin'])
async def join_voice(ctx):
    """Join the voice channel you're in"""
    if not ctx.author.voice:
        await ctx.send("❌ You need to be in a voice channel!")
        return
    
    channel = ctx.author.voice.channel
    
    try:
        vc = await channel.connect()
        
        # Automatically enable listening
        listening_channels.add(channel.id)
        
        await ctx.send(f"🎙️ **Connected to {channel.name}!**\n"
                      f"💬 **How to use:**\n"
                      f"• Type messages and I'll speak them!\n"
                      f"• Mention me or just chat normally\n"
                      f"• I'll respond with both text and voice\n\n"
                      f"⚠️ **Note:** Discord doesn't support bots receiving voice audio.\n"
                      f"For voice-to-voice, you'll need external audio capture tools.")
        
        print(f"✅ Connected to voice channel: {channel.name}")
        print(f"🎧 Auto-respond enabled - will speak responses to text messages")
        
    except Exception as e:
        await ctx.send(f"❌ Failed to connect: {e}")
        print(f"❌ Connection error: {e}")


async def finished_callback(sink, channel, *args):
    """Called when recording stops"""
    print("🛑 Recording finished")


@bot.command(name='leave', aliases=['vleave'])
async def leave_voice(ctx):
    """Leave the current voice channel"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Disconnected from voice")
    else:
        await ctx.send("❌ Not in a voice channel")


@bot.command(name='listen', aliases=['vlisten'])
async def start_listening(ctx):
    """Start actively listening for voice"""
    if not ctx.voice_client:
        await ctx.send("❌ Not in a voice channel! Use `!join` first")
        return
    
    channel_id = ctx.voice_client.channel.id
    listening_channels.add(channel_id)
    
    await ctx.send("🎧 **Voice listening activated!**\n\n"
                   "I'm now listening to voice in this channel.\n"
                   "⚠️ Note: Discord voice receiving is experimental and may have limitations.")
    
    print(f"🎧 Started listening in channel {channel_id}")


@bot.command(name='speak', aliases=['vspeak', 'say'])
async def speak_command(ctx, *, text: str = None):
    """Make the bot speak in voice channel"""
    if not text:
        await ctx.send("Please provide text to speak! Usage: `!speak hello`")
        return
    
    if not ctx.voice_client:
        await ctx.send("❌ Not in a voice channel! Use `!join` first")
        return
    
    await speak_text(ctx.voice_client, text)
    await ctx.send(f"🗣️ Speaking: *{text[:100]}*")


async def speak_text(voice_client, text: str):
    """Generate TTS and play in voice channel"""
    try:
        # Generate TTS audio
        temp_dir = tempfile.gettempdir()
        audio_path = os.path.join(temp_dir, f"nova_voice_bot_{os.getpid()}.mp3")
        
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(audio_path)
        
        # Stop current playback if any
        if voice_client.is_playing():
            voice_client.stop()
            await asyncio.sleep(0.2)
        
        # Play audio
        audio_source = discord.FFmpegPCMAudio(audio_path)
        voice_client.play(audio_source, after=lambda e: cleanup_audio(audio_path, e))
        
        print(f"🎤 Speaking: {text[:50]}...")
        
    except Exception as e:
        print(f"❌ TTS error: {e}")


def cleanup_audio(path: str, error):
    """Clean up temp audio file"""
    try:
        if os.path.exists(path):
            os.remove(path)
    except:
        pass
    if error:
        print(f"❌ Playback error: {error}")


async def get_ai_response(user_message: str, username: str) -> str:
    """Get response from Ollama"""
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": "llama3.2-vision",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are Nova, a helpful AI assistant in a voice channel. Keep responses brief and conversational (1-3 sentences max for voice). Be friendly and natural."
                    },
                    {
                        "role": "user",
                        "content": f"{username} says: {user_message}"
                    }
                ],
                "stream": False
            }
            
            async with session.post(f"{OLLAMA_URL}/api/chat", json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("message", {}).get("content", "I didn't catch that, sorry!")
                else:
                    return "Sorry, I'm having trouble thinking right now."
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        return "Sorry, something went wrong!"


async def transcribe_voice(audio_data: bytes) -> str:
    """Transcribe voice audio to text using Whisper (for future use)"""
    try:
        # Save audio to temp file
        temp_dir = tempfile.gettempdir()
        audio_path = os.path.join(temp_dir, f"voice_input_{os.getpid()}.wav")
        
        with open(audio_path, 'wb') as f:
            f.write(audio_data)
        
        # Transcribe with Whisper
        result = whisper_model.transcribe(audio_path, fp16=False)
        text = result["text"].strip()
        
        # Clean up
        try:
            os.remove(audio_path)
        except:
            pass
        
        return text
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        return None


@bot.event
async def on_message(message):
    """Handle messages - auto-respond in voice if enabled"""
    # Debug logging
    print(f"📨 Message received: {message.author.name}: {message.content[:50]}")
    
    if message.author == bot.user:
        print("⏭️ Ignoring own message")
        return
    
    # Process commands first
    await bot.process_commands(message)
    
    # Skip command messages
    if message.content.startswith('!'):
        print("⏭️ Skipping command message")
        return
    
    # If we're in a voice channel in this server and auto-respond is on
    if auto_respond and bot.voice_clients:
        print(f"🔍 Checking voice clients... auto_respond={auto_respond}, voice_clients={len(bot.voice_clients)}")
        
        for vc in bot.voice_clients:
            print(f"   Voice client in guild: {vc.guild.name}, channel: {vc.channel.name} (ID: {vc.channel.id})")
            print(f"   Message guild: {message.guild.name if message.guild else 'DM'}")
            print(f"   Listening channels: {listening_channels}")
            
            if vc.guild == message.guild and vc.channel.id in listening_channels:
                print(f"✅ Conditions met! Processing message...")
                
                # Get AI response
                response = await get_ai_response(message.content, message.author.display_name)
                
                print(f"🤖 Nova responds: {response}")
                
                # Speak the response
                await speak_text(vc, response)
                
                # Also send text response
                await message.channel.send(f"🗣️ {response}")
                break
            else:
                print(f"❌ Conditions not met for this voice client")
    else:
        if not auto_respond:
            print("⏭️ Auto-respond is disabled")
        if not bot.voice_clients:
            print("⏭️ Not in any voice channels")


@bot.command(name='voicestatus', aliases=['vstatus'])
async def voice_status(ctx):
    """Check voice bot status"""
    status = "🎙️ **Nova Voice Bot Status**\n\n"
    
    if ctx.voice_client:
        status += f"**Connected:** ✅ {ctx.voice_client.channel.name}\n"
        status += f"**Members:** {len(ctx.voice_client.channel.members)}\n"
        status += f"**Auto-Respond:** {'✅ ON' if auto_respond else '❌ OFF'}\n"
    else:
        status += "**Connected:** ❌ Not in voice\n"
    
    status += f"**Listening Channels:** {len(listening_channels)}\n\n"
    status += "**Commands:**\n"
    status += "`!join` - Join voice (auto-listens)\n"
    status += "`!speak <text>` - Speak\n"
    status += "`!listen` - Toggle listening\n"
    status += "`!leave` - Leave voice\n"
    
    await ctx.send(status)


@bot.command(name='autorespond', aliases=['auto'])
async def toggle_autorespond(ctx, state: str = None):
    """Toggle automatic voice responses"""
    global auto_respond
    
    if state:
        if state.lower() in ['on', 'true', '1', 'yes']:
            auto_respond = True
            await ctx.send("✅ Auto-respond **enabled** - I'll respond to text messages with voice")
        elif state.lower() in ['off', 'false', '0', 'no']:
            auto_respond = False
            await ctx.send("❌ Auto-respond **disabled** - Use `!speak` to make me talk")
    else:
        auto_respond = not auto_respond
        status = "enabled" if auto_respond else "disabled"
        await ctx.send(f"Auto-respond is now **{status}**")


# Main entry point
if __name__ == "__main__":
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("❌ DISCORD_BOT_TOKEN not found in .env file!")
        exit(1)
    
    print("🚀 Starting Nova Voice Bot...")
    bot.run(token)
