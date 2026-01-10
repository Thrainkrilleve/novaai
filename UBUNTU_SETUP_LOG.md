# Ubuntu Home Server Setup Log

This document tracks the setup and troubleshooting steps for deploying Nova on Ubuntu home server.

## Server Configuration

**Directory Structure:**
```
/nova/novaai-main/
├── backend/
│   ├── .env
│   ├── discord_bot.py
│   ├── main.py
│   ├── requirements.txt
│   └── venv/
├── frontend/
└── ...
```

## Environment Configuration

**File: `/nova/novaai-main/backend/.env`**
```bash
DISCORD_TOKEN=YOUR_DISCORD_TOKEN_HERE
DISCORD_BOT_TOKEN=YOUR_DISCORD_BOT_TOKEN_HERE

# Ollama settings
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2-vision
OLLAMA_TEMPERATURE=0.8

# VPS Mode (set to false for home server to enable all features)
VPS_MODE=false
```

## Running Nova

### Manual Start
```bash
cd /nova/novaai-main/backend
source venv/bin/activate
python discord_bot.py
```

### As Systemd Service
```bash
# Start
sudo systemctl start nova-discord

# Stop
sudo systemctl stop nova-discord

# Restart
sudo systemctl restart nova-discord

# Check status
sudo systemctl status nova-discord

# View logs
sudo journalctl -u nova-discord -f
```

## Troubleshooting

### Issue: "Ollama is not running"

**Cause:** Model mismatch between .env and installed models

**Solution:**
1. Check installed models:
   ```bash
   ollama list
   ```

2. Check what's in .env:
   ```bash
   cat /nova/novaai-main/backend/.env
   ```

3. Verify Ollama API is accessible:
   ```bash
   curl http://localhost:11434/api/version
   curl http://localhost:11434/api/tags
   ```

4. Pull the correct model:
   ```bash
   ollama pull llama3.2-vision
   ```

5. Restart the bot after pulling new model

### Issue: Python can't find discord_bot.py

**Cause:** Running from wrong directory

**Solution:** Must run from backend directory:
```bash
cd /nova/novaai-main/backend
python discord_bot.py
```

### Systemd Service Configuration

**File: `/etc/systemd/system/nova-discord.service`**
```ini
[Unit]
Description=Nova AI Discord Bot
After=network.target ollama.service

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/nova/novaai-main/backend
Environment="PATH=/nova/novaai-main/backend/venv/bin"
ExecStart=/nova/novaai-main/backend/venv/bin/python discord_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**After editing service file:**
```bash
sudo systemctl daemon-reload
sudo systemctl restart nova-discord
```

## Ollama Configuration

### Check Ollama Status
```bash
systemctl status ollama
```

### Check Ollama Port
```bash
sudo netstat -tlnp | grep ollama
# or
sudo ss -tlnp | grep ollama
```

### Installed Models
- **llama3.2-vision** - Vision-capable model (7.8 GB) - RECOMMENDED
- **llama3.2:3b** - Text-only model (lighter, no vision)

### Pull Vision Model
```bash
ollama pull llama3.2-vision
```

## Network Access

### Discord Bot
- ✅ Works from anywhere (connects outbound to Discord)
- ✅ No port forwarding needed
- ✅ Access from any device with Discord

### Web API (Optional)
- 🏠 Local network only by default (http://SERVER-IP:8000)
- Would need port forwarding + domain setup for external access
- Recommended: Use Discord bot for remote access

## Python Virtual Environment

### Create venv
```bash
cd /nova/novaai-main
python3 -m venv venv
```

### Activate venv
```bash
source venv/bin/activate
```

### Install dependencies
```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt
```

## Useful Commands

### Update Nova Code
```bash
sudo systemctl stop nova-discord
cd /nova/novaai-main
git pull
source venv/bin/activate
cd backend
pip install -r requirements.txt
sudo systemctl start nova-discord
```

### Check Logs
```bash
# Last 100 lines
sudo journalctl -u nova-discord -n 100

# Follow in real-time
sudo journalctl -u nova-discord -f

# Show errors only
sudo journalctl -u nova-discord -p err
```

### Verify Setup
```bash
# Check Python
python3 --version

# Check Ollama
ollama --version
systemctl status ollama

# Check models
ollama list

# Test Ollama API
curl http://localhost:11434/api/version
curl http://localhost:11434/api/tags

# Check venv packages
source venv/bin/activate
pip list
```

## Key Learnings

1. **Model names must match exactly** - Check `ollama list` output vs OLLAMA_MODEL in .env
2. **.env must be in backend directory** - Where Python scripts run from
3. **Ollama runs on port 11434 by default** - Make sure OLLAMA_HOST points to http://localhost:11434
4. **Must restart bot after pulling new models** - Bot checks model availability on startup
5. **Working directory matters** - Always cd to /nova/novaai-main/backend before running
6. **Home server = VPS_MODE=false** - Enables all features (screen capture, browser, etc.)

## Setup Date
January 10, 2026

## Related Documentation
- [UBUNTU_HOME_SERVER_SETUP.md](UBUNTU_HOME_SERVER_SETUP.md) - Complete setup guide
- [QUICKSTART_VPS.md](QUICKSTART_VPS.md) - VPS deployment guide
- [README.md](README.md) - General Nova documentation
