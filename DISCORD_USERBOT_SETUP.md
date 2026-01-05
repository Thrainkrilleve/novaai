# Discord Self-Bot Setup (No BOT Badge)

⚠️ **IMPORTANT**: This runs on your Discord user account, not a bot account. This means **no "BOT" badge** and it appears as you. Discord's ToS prohibits user account automation for spam/disruption. Use responsibly for personal purposes only.

⚠️ **PYTHON VERSION**: discord.py-self currently only works with Python 3.11 or 3.12. Python 3.14 has compatibility issues. If you're on Python 3.14, either downgrade Python or use the regular bot account method (see bottom of this guide).

---

## Quick Setup

### 1. Get Your Discord Token

**Open Discord in Browser** (must be web version, not desktop app):
1. Go to [discord.com](https://discord.com)  
2. Login to your account
3. Press `F12` (or `Ctrl+Shift+I`) to open DevTools
4. Go to the **Application** tab (or **Storage** in Firefox)
5. In the left sidebar, expand **Local Storage** → Click **https://discord.com**
6. In the filter box, type: `token`
7. Look for the key named `token` - the value is your token (long string in quotes)
8. **Double-click** the value to select it, then copy (remove the quotes)
9. **🔒 Keep this secret! Never share it!**

**Alternative Method (Console):**
If the above doesn't work, try this in the **Console** tab:
```javascript
(webpackChunkdiscord_app.push([[''],{},e=>{m=[];for(let c in e.c)m.push(e.c[c])}]),m).find(m=>m?.exports?.default?.getToken!==void 0).exports.default.getToken()
```
Or simpler:
```javascript
window.localStorage.token.replace(/"/g, "")
```

### 2. Add Token to .env

```powershell
cd H:\TheAI\backend
notepad .env
```

Add this line:
```
DISCORD_TOKEN=paste_your_token_here
```

Save and close.

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Run It

```powershell
python discord_bot.py
```

You should see:
```
✅ Logged in as YourName#1234
🤖 Using Ollama model: llama3.2-vision
```

---

## How to Use

The bot responds to `!` commands in any channel you can access:

**Basic Commands:**
```
!chat What's the meaning of life?
!screen What do you see on my screen?
!browse https://docs.python.org
!search python decorators tutorial
!history
!clear
!help
```

**Examples:**
- `!chat explain quantum computing simply`
- `!screen is there an error?`
- `!browse https://github.com/trending`
- `!search best practices for async python`

---

## Key Differences from Bot Account

| Feature | Self-Bot (Current) | Bot Account |
|---------|-------------------|-------------|
| Badge | ❌ None (appears as you) | ✅ Shows "BOT" badge |
| Access | All channels you can access | Only where invited |
| Appearance | You talking to yourself | Clearly a bot |
| ToS | ⚠️ Gray area | ✅ Allowed |
| Setup | Just token | Portal + OAuth2 |

---

## Safety & Best Practices

**🔒 Security:**
- Never share your token
- `.env` is in `.gitignore` (won't be committed)
- If token leaks, change your Discord password immediately

**⏱️ Rate Limits:**
- Don't spam commands
- Discord may temporarily ban your account for excessive API calls
- Wait a few seconds between commands

**📸 Privacy:**
- `!screen` captures your ENTIRE screen
- Be aware what's visible when using it
- Close sensitive information before using

**⚖️ Responsible Use:**
- Use in private servers or DMs
- Don't use for spam, harassment, or disruption
- Don't advertise this as a public bot
- Keep it personal/private

---

## Troubleshooting

**"Improper token has been passed"**
- Token is invalid/expired
- Get a fresh token using the browser console method
- Make sure you copied the entire token

**Bot not responding**
- Check `python discord_bot.py` is running
- Verify `.env` has correct token
- Ensure Ollama is running locally

**Rate limited / "You are being rate limited"**
- You sent too many commands too quickly
- Wait 5-10 minutes
- Slow down command usage

**Import error for discord**
- Run: `pip install --force-reinstall discord.py-self`
- Make sure you're using `discord.py-self` not regular `discord.py`

---

## Want a Real Bot Instead?

If you prefer an official bot account (with BOT badge):

### Switch to Bot Mode:

1. **Edit requirements.txt:**
```diff
- discord.py-self>=2.1.0
+ discord.py>=2.4.0
```

2. **Edit discord_bot.py (line ~20):**
```diff
  bot = commands.Bot(
      command_prefix='!',
      intents=intents,
-     self_bot=True,
      description='Local AI Assistant'
  )
```

3. **Create Bot Account:**
   - [Discord Developer Portal](https://discord.com/developers/applications)
   - New Application → Bot → Add Bot
   - Copy bot token
   - Enable "Message Content Intent"

4. **Invite Bot:**
   - OAuth2 → URL Generator
   - Scopes: `bot`
   - Permissions: Send Messages, Read Messages, Attach Files
   - Open generated URL → Authorize to your server

5. **Update .env with bot token**

6. **Reinstall & run:**
```powershell
pip install -r requirements.txt
python discord_bot.py
```

---

## How It Works

```
Discord (Your Account)
    ↓
discord.py-self (Python client)
    ↓
Command Parser (!chat, !screen, etc.)
    ↓
┌─────────────┬──────────────┬──────────────┐
│ Ollama AI   │ Screen Cap   │ Web Browser  │
│ (Vision)    │ (mss)        │ (Playwright) │
└─────────────┴──────────────┴──────────────┘
    ↓
Response sent back to Discord
```

**Your Discord account** → **Python script** → **Local AI** → **Response**

No data leaves your computer except Discord messages!
