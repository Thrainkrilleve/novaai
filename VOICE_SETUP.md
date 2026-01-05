# 🎙️ Nova Voice Features Setup

Nova now has voice capabilities! She can speak in voice channels and understand speech.

## Features

- **Text-to-Speech (TTS)** - Nova can speak your messages in voice channels
- **Speech-to-Text (STT)** - Nova can listen and transcribe voice (coming soon)
- **Voice Channel Integration** - Join/leave voice channels with commands

## Installation

### 1. Install Voice Dependencies

```powershell
cd H:\TheAI\backend
pip install pyttsx3 faster-whisper PyNaCl
```

### 2. Install FFmpeg (Required for Discord Voice)

**Option A: Chocolatey (Recommended)**
```powershell
choco install ffmpeg
```

**Option B: Manual Installation**
1. Download from: https://www.gyan.dev/ffmpeg/builds/
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your PATH environment variable
4. Restart terminal

**Verify Installation:**
```powershell
ffmpeg -version
```

### 3. Restart Nova

```powershell
cd H:\TheAI\backend
.\run_bot_autorestart.bat
```

## Usage

### Basic Voice Commands

**Join Voice Channel:**
```
!join
```
- You must be in a voice channel first
- Nova will join your current channel

**Make Nova Speak:**
```
!speak Hello everyone, I'm Nova!
!speak What would you like to talk about?
```

**Leave Voice Channel:**
```
!leave
```

**Check Voice Status:**
```
!voicestatus
```
- Shows TTS/STT availability
- Shows current voice connections
- Lists available commands

### Example Workflow

1. Join a voice channel in Discord
2. Type `!join` - Nova connects
3. Type `!speak Hey everyone!` - Nova speaks
4. Have conversations with `!speak` commands
5. Type `!leave` when done

## Voice Aliases

- `!join` = `!joinvc` = `!joinvoice`
- `!leave` = `!leavevc` = `!disconnect`
- `!speak` = `!say` = `!talk`
- `!voicestatus` = `!vcstatus` = `!voiceinfo`

## Limitations

⚠️ **Important Notes:**

1. **discord.py-self Voice Support**: The userbot library (discord.py-self) has limited voice support compared to regular bots. Voice features may not work in all scenarios.

2. **FFmpeg Required**: Discord voice requires FFmpeg for audio encoding/decoding.

3. **TTS Voice Quality**: pyttsx3 uses system TTS engines (basic quality). For better quality, consider alternatives like:
   - Coqui TTS (local, high quality)
   - ElevenLabs API (cloud, very high quality)
   - Azure/Google TTS APIs

4. **STT Coming Soon**: Speech-to-Text (listening to voice) is implemented but needs testing. Use with `!listen` command (experimental).

## Troubleshooting

### "Voice features not available"
- Install dependencies: `pip install pyttsx3 PyNaCl`
- Install FFmpeg and add to PATH
- Restart Nova

### "Failed to join voice channel"
- Make sure you're in a voice channel first
- discord.py-self may not support voice in all server types
- Try a different voice channel

### "TTS not available"
- Install pyttsx3: `pip install pyttsx3`
- On Linux: `sudo apt-get install espeak`
- On macOS: System TTS should work out of the box

### No Audio Playing
- Check FFmpeg is installed: `ffmpeg -version`
- Check Discord voice settings (output device)
- Try adjusting TTS rate/volume in [voice_client.py](backend/voice_client.py)

## Advanced Configuration

### Customize TTS Voice

Edit [voice_client.py](backend/voice_client.py):

```python
# Change voice (line ~47)
for voice in voices:
    if 'david' in voice.name.lower():  # Change to preferred voice name
        self.tts_engine.setProperty('voice', voice.id)
        break

# Adjust speed (line ~50)
self.tts_engine.setProperty('rate', 175)  # 150-200 recommended

# Adjust volume (line ~51)
self.tts_engine.setProperty('volume', 0.9)  # 0.0-1.0
```

### Use Better TTS

For higher quality voice, consider integrating:

**Coqui TTS (Local, Free):**
```python
pip install TTS
# Implement in voice_client.py
```

**ElevenLabs (Cloud, Paid):**
```python
pip install elevenlabs
# Add API key and implement
```

## Future Enhancements

- 🎧 **Active Listening** - Nova joins voice and listens to conversations
- 🤖 **Auto-Speak** - Nova can interject in voice conversations autonomously
- 🎵 **Music Player** - Play music/sounds in voice channels
- 🔊 **Voice Effects** - Apply filters/effects to Nova's voice
- 🗣️ **Multi-Voice** - Different voices for different moods
- 🎙️ **Voice Commands** - Control Nova with voice ("Hey Nova...")

## Testing

Test voice features:
```
!voicestatus          # Check what's available
!join                 # Join your channel
!speak Testing 1 2 3  # Test TTS
!speak I am Nova, your AI assistant running locally on your computer
!leave                # Disconnect
```

## Need Help?

- Check voice status: `!voicestatus`
- Review this guide
- Check console logs for errors
- Verify FFmpeg installation
- Try reinstalling voice dependencies

---

**Nova Voice is experimental** - Some features may not work perfectly with discord.py-self. Regular bots have better voice support.
