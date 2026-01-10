# 🏠 Nova AI - Ubuntu Home Server Setup Guide

Complete guide to deploy Nova AI on your Ubuntu home server.

## 📋 Prerequisites

- Ubuntu Server 20.04+ or Ubuntu Desktop
- At least 8GB RAM (16GB+ recommended for vision models)
- Python 3.10+
- Internet connection
- Discord token (for bot features)

## 🚀 Installation Steps

### Step 1: Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### Step 2: Install Python and Dependencies

```bash
# Install Python 3.10+ and pip
sudo apt install python3 python3-pip python3-venv git -y

# Verify Python version
python3 --version  # Should be 3.10 or higher
```

### Step 3: Install Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version

# Pull an AI model (choose based on your RAM)
# For 8GB RAM:
ollama pull llama3.2:3b

# For 16GB+ RAM (recommended, includes vision):
ollama pull llama3.2-vision

# Check that Ollama is running
systemctl status ollama
```

### Step 4: Clone/Upload Nova

```bash
# Create directory
sudo mkdir -p /opt/nova
sudo chown $USER:$USER /opt/nova
cd /opt/nova

# Option A: Clone from git (if you have a repo)
# git clone https://github.com/yourusername/nova.git .

# Option B: Upload files manually
# - Use SCP, SFTP, or file sharing to copy your Nova files
# - On Windows, you can use WinSCP or FileZilla
# Example: scp -r h:\TheAI/* username@server-ip:/opt/nova/
```

### Step 5: Setup Python Virtual Environment

```bash
cd /opt/nova

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install Python dependencies
cd backend
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 6: Configure Environment

```bash
# Create .env file
cd /opt/nova/backend
nano .env
```

Add the following configuration (adjust as needed):

```bash
# Server Settings
HOST=0.0.0.0
PORT=8000

# Ollama Settings
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2-vision
OLLAMA_TEMPERATURE=0.8

# Discord Settings (get your token from Discord)
DISCORD_TOKEN=YOUR_DISCORD_TOKEN_HERE
DISCORD_BOT_TOKEN=YOUR_BOT_TOKEN_IF_YOU_HAVE_ONE
DISCORD_COMMAND_PREFIX=!

# Database
DATABASE_URL=sqlite+aiosqlite:///./chatbot.db

# VPS Mode (set to false for home server to enable all features)
VPS_MODE=false

# Optional: Domain settings (if you have a domain pointing to your server)
DOMAIN=
FRONTEND_URL=
```

**Save and exit** (Ctrl+X, then Y, then Enter)

### Step 7: Test Run

```bash
# Make sure you're in the backend directory with venv activated
cd /opt/nova/backend
source ../venv/bin/activate

# Test the Discord bot
python discord_bot.py

# OR test the web API
python main.py
```

If everything works, press `Ctrl+C` to stop and proceed to set up systemd services.

### Step 8: Create Systemd Service (Run 24/7)

Create a service file for automatic startup:

```bash
sudo nano /etc/systemd/system/nova-discord.service
```

Add this content:

```ini
[Unit]
Description=Nova AI Discord Bot
After=network.target ollama.service

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/opt/nova/backend
Environment="PATH=/opt/nova/venv/bin"
ExecStart=/opt/nova/venv/bin/python discord_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Replace `YOUR_USERNAME` with your actual Ubuntu username**

Save and exit (Ctrl+X, then Y, then Enter)

Enable and start the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable nova-discord

# Start the service
sudo systemctl start nova-discord

# Check status
sudo systemctl status nova-discord
```

### Step 9: (Optional) Setup Web API Service

If you want the web interface running too:

```bash
sudo nano /etc/systemd/system/nova-web.service
```

Add this content:

```ini
[Unit]
Description=Nova AI Web API
After=network.target ollama.service

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/opt/nova/backend
Environment="PATH=/opt/nova/venv/bin"
ExecStart=/opt/nova/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable nova-web
sudo systemctl start nova-web
sudo systemctl status nova-web
```

### Step 10: Configure Firewall (Optional but Recommended)

```bash
# Allow SSH
sudo ufw allow 22

# Allow web API (if running web service)
sudo ufw allow 8000

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

## 📊 Useful Commands

### Check Service Status
```bash
# Discord bot status
sudo systemctl status nova-discord

# Web API status
sudo systemctl status nova-web

# Ollama status
systemctl status ollama
```

### View Logs
```bash
# Discord bot logs
sudo journalctl -u nova-discord -f

# Web API logs
sudo journalctl -u nova-web -f

# Ollama logs
sudo journalctl -u ollama -f
```

### Restart Services
```bash
sudo systemctl restart nova-discord
sudo systemctl restart nova-web
sudo systemctl restart ollama
```

### Stop Services
```bash
sudo systemctl stop nova-discord
sudo systemctl stop nova-web
```

### Update Nova
```bash
# Stop services
sudo systemctl stop nova-discord
sudo systemctl stop nova-web

# Update code (if using git)
cd /opt/nova
git pull

# Or upload new files manually

# Reinstall dependencies (if requirements.txt changed)
source venv/bin/activate
cd backend
pip install -r requirements.txt

# Restart services
sudo systemctl start nova-discord
sudo systemctl start nova-web
```

## 🔧 Troubleshooting

### Check if Ollama is Running
```bash
systemctl status ollama
curl http://localhost:11434/api/version
```

### Test Ollama Model
```bash
ollama list  # See installed models
ollama run llama3.2-vision "Hello, how are you?"
```

### Check Python Dependencies
```bash
cd /opt/nova
source venv/bin/activate
pip list
```

### View Detailed Error Logs
```bash
# Last 100 lines of Discord bot logs
sudo journalctl -u nova-discord -n 100

# Follow logs in real-time
sudo journalctl -u nova-discord -f
```

### Permission Issues
```bash
# Make sure your user owns the Nova directory
sudo chown -R $USER:$USER /opt/nova

# Make sure database directory is writable
cd /opt/nova/backend
chmod 755 .
```

## 🌐 Access from Other Devices

### Local Network Access

The web API will be accessible at:
- From the server: `http://localhost:8000`
- From other devices on your network: `http://SERVER-IP:8000`

Find your server IP:
```bash
hostname -I
```

### Discord Bot

Once the Discord bot is running, it will respond in Discord according to the channel modes configured. No additional network setup needed.

## 🎯 Next Steps

1. **Test Discord Integration**: Send a message in a Discord channel where Nova is active
2. **Configure Channel Modes**: Use `!mode smart` to set how Nova responds
3. **Try Voice Features**: Join a voice channel with Nova (if voice features are enabled)
4. **VS Code Integration**: Set up the VS Code client if needed
5. **Learning System**: Nova will remember facts about users automatically

## 📖 Related Documentation

- [Discord Setup](DISCORD_USERBOT_SETUP.md)
- [Voice Setup](VOICE_SETUP.md)
- [VS Code Integration](VSCODE_INTEGRATION_SETUP.md)
- [Learning System](LEARNING_SYSTEM.md)
- [Autonomous Features](NOVA_AUTONOMOUS_FEATURES.md)

## 🆘 Getting Help

If you run into issues:

1. Check the service logs: `sudo journalctl -u nova-discord -n 100`
2. Verify Ollama is running: `systemctl status ollama`
3. Check Python dependencies: `pip list` (in activated venv)
4. Verify .env configuration
5. Make sure your Discord token is valid

## 🔄 Keeping Nova Running

The systemd services will:
- ✅ Auto-start on server boot
- ✅ Auto-restart if Nova crashes
- ✅ Run in the background
- ✅ Persist across SSH sessions

You can now safely close your SSH session and Nova will keep running!
