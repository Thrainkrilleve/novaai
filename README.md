# 🤖 Nova AI Assistant

A powerful, self-hosted AI assistant with Discord integration, learning capabilities, and multiple deployment options.

## ✨ Features

- 🤖 **Local LLM** - Runs entirely on your machine using Ollama
- 💬 **Dual Interface** - Web UI or Discord Bot
- 🧠 **Learning System** - Remembers facts about users and conversations
- 🎙️ **Voice Features** - Text-to-speech and voice channel support
- 🎮 **EVE Online Helper** - Built-in EVE SDE database integration
- 💻 **VS Code Integration** - Control VS Code from Discord
- 🤖 **Autonomous Agent** - Can perform tasks independently
- 🔒 **Privacy First** - All data stays on your machine

## 📋 Prerequisites

- **Python 3.10+**
- **Ollama** - [Install from ollama.com](https://ollama.com)
- **Node.js 18+** (optional, for web frontend)

## 🚀 Quick Start

### 1. Install Ollama

```bash
# Download from https://ollama.com
# Pull a model
ollama pull llama3.2:3b        # For 8GB RAM
# OR
ollama pull llama3.2-vision    # For 16GB+ RAM
```

### 2. Setup Backend

```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure

```bash
cp .env.example .env
# Edit .env and add your settings (at minimum: OLLAMA_MODEL)
```

### 4. Run

```bash
# Discord Bot
python discord_bot.py

# OR Web API
python main.py
```

## 🌐 Deployment Options

### Option 1: Local Development

Perfect for testing and local use with full features.

```bash
cd backend
python main.py
```

Access at: `http://localhost:8000`

### Option 2: VPS Deployment (Production)

Deploy to Hostinger, DigitalOcean, or any VPS with Cloudflare integration.

**Quick Deploy (30 minutes):**
```bash
# See quick start guide
cat QUICKSTART_VPS.md
```

**Detailed Guide:**
```bash
# Complete deployment instructions
cat HOSTINGER_DEPLOYMENT.md
```

**What changes in VPS mode:**
- ✅ Runs 24/7
- ✅ Global CDN via Cloudflare
- ✅ DDoS protection
- ⚠️ Screen capture disabled
- ⚠️ Browser automation disabled

See [VPS_OPTIMIZATION_SUMMARY.md](VPS_OPTIMIZATION_SUMMARY.md) for details.

## 📚 Documentation

- **[Quick Start (VPS)](QUICKSTART_VPS.md)** - 30-minute deployment guide
- **[Hostinger Deployment](HOSTINGER_DEPLOYMENT.md)** - Complete VPS setup
- **[Subdomain Setup](SUBDOMAIN_SETUP.md)** - Use subdomain with existing Worker
- **[VPS Optimization](VPS_OPTIMIZATION_SUMMARY.md)** - What changed for cloud
- **[Discord Setup](DISCORD_USERBOT_SETUP.md)** - Configure Discord bot
- **[Voice Setup](VOICE_SETUP.md)** - Enable voice features
- **[VS Code Integration](VSCODE_INTEGRATION_SETUP.md)** - Connect to VS Code
- **[Learning System](LEARNING_SYSTEM.md)** - How memory works
- **[API Documentation](backend/API_DOCUMENTATION.md)** - REST API reference

## 🎮 Discord Commands

### Chat Commands
- `!chat <message>` - Chat with Nova
- `!ask <question>` - Quick question
- `!clear` - Clear conversation history
- `!memory` - View conversation stats

### Learning & Memory
- `!learn <fact>` - Teach Nova something
- `!profile` - View what Nova knows about you
- `!remember <fact>` - Save important information

### Code Generation
- `!codegen <description>` - Generate code
- `!createfile <filename>` - Create and populate a file

### EVE Online
- `!eve search <item>` - Search EVE items
- `!eve ship <name>` - Get ship information
- `!eve item <name>` - Get item details

### Voice
- `!join` - Join voice channel
- `!speak <text>` - Text-to-speech
- `!leave` - Leave voice channel

### Utility
- `!status` - Check bot status
- `!aihelp` - Show all commands
- `!autonomous` - Manage autonomous agent

### Disabled in VPS Mode
- `!screen` - Screen capture (local only)
- `!browse <url>` - Web browsing (local only)
- `!video <url>` - Video analysis (local only)

## ⚙️ Configuration

Edit `.env` file:

```env
# Server
HOST=0.0.0.0
PORT=8000

# Ollama
OLLAMA_MODEL=llama3.2:3b

# Discord
DISCORD_TOKEN=your_token_here

# Production (optional)
DOMAIN=yourdomain.com
```

## 📊 System Requirements

### Minimum (Local/VPS)
- **CPU**: 2 cores
- **RAM**: 8 GB
- **Storage**: 50 GB
- **Model**: llama3.2:3b
- **Response**: 10-30s

### Recommended
- **CPU**: 4 cores
- **RAM**: 16 GB
- **Storage**: 100 GB
- **Model**: llama3.2-vision
- **Response**: 5-20s

### With GPU (Best)
- **GPU**: NVIDIA RTX 3060+ (8GB VRAM)
- **Response**: 1-5s

## 🔧 Architecture

```
┌─────────────────────────────────────┐
│         Frontend (Optional)         │
│     React + Vite + TailwindCSS      │
└─────────────────────────────────────┘
              ↕ HTTP/WebSocket
┌─────────────────────────────────────┐
│         Backend (FastAPI)           │
│  ├─ Chat Handler                    │
│  ├─ Discord Bot                     │
│  ├─ Learning System                 │
│  ├─ Autonomous Agent                │
│  └─ Voice Client                    │
└─────────────────────────────────────┘
              ↕
┌─────────────────────────────────────┐
│         Ollama (Local LLM)          │
│     llama3.2:3b / phi-3-mini        │
└─────────────────────────────────────┘
```

## 🛠️ Development

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run in development
python main.py

# Run Discord bot
python discord_bot.py
```

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## ⚠️ Disclaimer

Nova uses Discord's user token for userbot functionality. Be aware:
- User bots are against Discord's Terms of Service for official bots
- Use at your own risk
- For personal use only
- Consider using official bot tokens for production

## 🆘 Support

- **Issues**: Open an issue on GitHub
- **Documentation**: Check the docs in this repository
- **Deployment Help**: See QUICKSTART_VPS.md or HOSTINGER_DEPLOYMENT.md

## 🎉 Acknowledgments

- [Ollama](https://ollama.com) - Local LLM runtime
- [FastAPI](https://fastapi.tiangolo.com) - Web framework
- [discord.py-self](https://github.com/dolfies/discord.py-self) - Discord userbot library
- EVE Online SDE - Game data integration

---

Made with ❤️ for AI enthusiasts and EVE Online pilots

**Deploy to VPS**: [QUICKSTART_VPS.md](QUICKSTART_VPS.md)  
**Full Guide**: [HOSTINGER_DEPLOYMENT.md](HOSTINGER_DEPLOYMENT.md)
