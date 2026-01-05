# Nova VPS Deployment Guide (Hostinger + Cloudflare)

## ✅ What Was Changed

Nova has been optimized for VPS deployment with these modifications:

### Removed Features (No longer needed):
- ❌ Screen capture (`mss`, `Pillow`)
- ❌ Browser automation (`playwright`)
- ❌ `!screen`, `!screenshot`, `!browse`, `!web`, `!search` commands
- ❌ `!links`, `!extract`, `!pageinfo`, `!analyze`, `!video` commands

### What Still Works:
- ✅ Chat with Nova (!chat, !ask)
- ✅ Discord bot with learning
- ✅ Memory system (!memory, !learn)
- ✅ Code generation (!codegen, !createfile)
- ✅ EVE Online helper (!eve)
- ✅ Voice features (!speak, !join, !leave)
- ✅ Autonomous agent (!autonomous)
- ✅ VS Code integration
- ✅ Web API endpoints

### Added:
- ✅ Cloudflare proxy support (real IP extraction)
- ✅ Production-ready CORS configuration
- ✅ VPS mode indicators
- ✅ Bind to 0.0.0.0 for external access

---

## 🚀 Deployment Steps

### 1. Prepare Your VPS (Hostinger KVM)

SSH into your Hostinger VPS:
```bash
ssh root@your-vps-ip
```

Update system:
```bash
apt update && apt upgrade -y
```

Install Python 3.10+ and dependencies:
```bash
apt install python3 python3-pip python3-venv git -y
```

### 2. Install Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
systemctl start ollama
systemctl enable ollama

# Pull your model (choose one based on VPS specs)
# For 8GB RAM: Use smaller model
ollama pull llama3.2:3b
# OR for 16GB RAM: Use the vision model
ollama pull llama3.2-vision
```

### 3. Deploy Nova

```bash
# Create app directory
mkdir -p /opt/nova
cd /opt/nova

# Clone your repository (or upload files)
git clone <your-nova-repo-url> .
# OR upload via SCP/SFTP

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 4. Configure Environment

Create `.env` file:
```bash
cd /opt/nova/backend
nano .env
```

Add configuration:
```env
# Server
HOST=0.0.0.0
PORT=8000

# Production (optional - configure after Cloudflare setup)
DOMAIN=yourdomain.com
FRONTEND_URL=https://yourdomain.com

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
# OR for 16GB RAM VPS:
# OLLAMA_MODEL=llama3.2-vision

# Discord (optional)
DISCORD_TOKEN=your_discord_token_here

# Database
DATABASE_URL=sqlite+aiosqlite:////opt/nova/backend/chatbot.db
```

### 5. Create Systemd Service

Create service file:
```bash
nano /etc/systemd/system/nova.service
```

Add content:
```ini
[Unit]
Description=Nova AI Assistant
After=network.target ollama.service
Wants=ollama.service

[Service]
Type=simple
User=root
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
systemctl daemon-reload
systemctl enable nova
systemctl start nova
systemctl status nova
```

### 6. Configure Firewall

```bash
# Allow SSH (important!)
ufw allow 22/tcp

# Allow HTTP/HTTPS for Cloudflare
ufw allow 80/tcp
ufw allow 443/tcp

# Allow Nova API (if you want direct access)
ufw allow 8000/tcp

# Enable firewall
ufw enable
```

### 7. Install Nginx (Reverse Proxy)

```bash
apt install nginx -y
```

Create Nginx config:
```bash
nano /etc/nginx/sites-available/nova
```

Add:
```nginx
server {
    listen 80;
    server_name yourdomain.com;  # Replace with your domain

    # Allow large requests for file uploads
    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # WebSocket support
        proxy_read_timeout 86400;
    }
}
```

Enable site:
```bash
ln -s /etc/nginx/sites-available/nova /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

---

## 🌐 Cloudflare Setup

### Option A: Subdomain Setup (Recommended)

**Best if you already have a Worker or site on your main domain.**

### 1. Add DNS Record

In Cloudflare Dashboard → DNS:

| Type | Name | Content | Proxy | TTL |
|------|------|---------|-------|-----|
| A | `api` | Your VPS IP | ✅ Proxied | Auto |

This creates: `api.yourdomain.com`

**Alternative subdomain names:**
- `nova.yourdomain.com`
- `bot.yourdomain.com`
- `ai.yourdomain.com`

### 2. Update Nginx Configuration

```bash
nano /etc/nginx/sites-available/nova
```

Change `server_name`:
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;  # Change this line
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        # ... rest of config
    }
}
```

Restart Nginx:
```bash
nginx -t
systemctl restart nginx
```

### 3. Update Nova Configuration

```bash
cd /opt/nova/backend
nano .env
```

Update:
```env
DOMAIN=api.yourdomain.com
```

Restart Nova:
```bash
systemctl restart nova
```

### 4. SSL/TLS Settings

Go to SSL/TLS → Overview:
- **Encryption mode**: Full (recommended)

Cloudflare automatically provides SSL certificate.

**Your Architecture:**
```
yourdomain.com          → Existing Cloudflare Worker
api.yourdomain.com      → Nova Backend (VPS)
app.yourdomain.com      → Frontend (optional)
```

---

### Option B: Main Domain Setup

**Use this if Nova is your primary service.**

### 1. Add Domain to Cloudflare

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Click "Add a Site"
3. Enter your domain
4. Choose Free plan
5. Update nameservers at your domain registrar

### 2. Configure DNS

Add A record:
- **Type**: A
- **Name**: @ (root domain)
- **IPv4 address**: Your VPS IP
- **Proxy status**: ✅ Proxied (orange cloud)
- **TTL**: Auto

### 3. SSL/TLS Settings

Go to SSL/TLS → Overview:
- **Encryption mode**: Full (recommended) or Flexible

If using Full, install SSL cert on VPS:
```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d yourdomain.com
```

### 4. Update Nova Config

Update `/opt/nova/backend/.env`:
```env
DOMAIN=yourdomain.com
FRONTEND_URL=https://yourdomain.com
```

Restart Nova:
```bash
systemctl restart nova
```

---

### Additional Cloudflare Settings

### 5. Firewall Rules (Optional)

Go to Security → WAF:
- Create rule to allow only Cloudflare IPs if desired
- Rate limiting for API endpoints

### 6. Page Rules (Optional)

Create rules for caching:
```
URL: api.yourdomain.com/static/*
Cache Level: Cache Everything
```

### 7. SSL/TLS Edge Certificates

Enable:
- Always Use HTTPS
- Automatic HTTPS Rewrites
- Minimum TLS Version: 1.2

---

## 🧪 Testing

### Test Local API
```bash
curl http://localhost:8000/
```

### Test Through Nginx
```bash
curl http://your-vps-ip/
```

### Test Through Cloudflare
```bash
curl https://yourdomain.com/
```

### Test WebSocket
```bash
# Install websocat
curl -s https://github.com/vi/websocat/releases/download/v1.12.0/websocat.x86_64-unknown-linux-musl -o /usr/local/bin/websocat
chmod +x /usr/local/bin/websocat

# Test
websocat wss://yourdomain.com/ws
```

---

## 📊 Monitoring

### Check Nova Status
```bash
systemctl status nova
```

### View Logs
```bash
journalctl -u nova -f
```

### Check Ollama
```bash
systemctl status ollama
curl http://localhost:11434/api/tags
```

### Resource Usage
```bash
htop
# Or
top
```

---

## 🔄 Updates

To update Nova:
```bash
cd /opt/nova
git pull
systemctl restart nova
```

---

## ⚠️ Troubleshooting

### Nova won't start
```bash
# Check logs
journalctl -u nova -n 50

# Test manually
cd /opt/nova/backend
source /opt/nova/venv/bin/activate
python main.py
```

### Ollama not responding
```bash
systemctl restart ollama
ollama list
```

### High CPU usage
- Switch to smaller model: `llama3.2:3b` or `phi-3-mini`
- Reduce concurrent requests in Nova

### Out of memory
```bash
free -h
# If swap is low, add swap space:
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

---

## 📈 Performance Tips

1. **Use smaller model** for CPU-only inference:
   - `phi-3-mini` (3.8B) - Very fast
   - `llama3.2:3b` (3B) - Good balance
   
2. **Adjust concurrency** in Nova if needed

3. **Enable Cloudflare caching** for static assets

4. **Monitor with** `htop` and adjust resources

---

## 🎉 Success!

Your Nova AI is now deployed on Hostinger VPS with Cloudflare!

**Access:**
- API: `https://yourdomain.com`
- Discord: Bot runs automatically
- WebSocket: `wss://yourdomain.com/ws`

**Features Available:**
- ✅ Chat API
- ✅ Discord bot
- ✅ Learning system
- ✅ Voice features
- ✅ Code generation
- ✅ EVE Online helper
