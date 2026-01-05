# Quick Start: Deploy Nova to Hostinger VPS

## 🚀 Fast Track (30 minutes)

### Step 1: VPS Setup (5 min)
```bash
# SSH to VPS
ssh root@your-vps-ip

# Install essentials
apt update && apt upgrade -y
apt install python3 python3-pip python3-venv git nginx -y
```

### Step 2: Install Ollama (5 min)
```bash
# Install
curl -fsSL https://ollama.com/install.sh | sh

# Pull model (choose based on RAM)
ollama pull llama3.2:3b         # 8GB RAM
# OR
ollama pull llama3.2-vision     # 16GB+ RAM
```

### Step 3: Deploy Nova (5 min)
```bash
# Clone and setup
mkdir -p /opt/nova && cd /opt/nova
# Upload your files here or git clone

# Install
python3 -m venv venv
source venv/bin/activate
cd backend
pip install -r requirements.txt
```

### Step 4: Configure (2 min)
```bash
# Create .env
cat > .env << 'EOF'
HOST=0.0.0.0
PORT=8000
OLLAMA_MODEL=llama3.2:3b
DISCORD_TOKEN=your_token_here
EOF
```

### Step 5: Systemd Service (3 min)
```bash
cat > /etc/systemd/system/nova.service << 'EOF'
[Unit]
Description=Nova AI
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/nova/backend
Environment="PATH=/opt/nova/venv/bin"
ExecStart=/opt/nova/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable nova
systemctl start nova
```

### Step 6: Nginx (5 min)
```bash
cat > /etc/nginx/sites-available/nova << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
    }
}
EOF

ln -s /etc/nginx/sites-available/nova /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx
```

### Step 7: Firewall (2 min)
```bash
ufw allow 22
ufw allow 80
ufw allow 443
ufw enable
```

### Step 8: Cloudflare (3 min)

**Option A: Subdomain (Recommended if you have existing Worker)**
1. Go to Cloudflare Dashboard → DNS
2. Add A record:
   - Type: `A`
   - Name: `api` (or `nova`, `bot`, etc.)
   - IPv4: Your VPS IP
   - Proxy: ✅ Proxied (orange cloud)
3. Update `.env`: `DOMAIN=api.yourdomain.com`
4. Update Nginx: `server_name api.yourdomain.com;`
5. SSL/TLS → Full mode
6. Restart: `systemctl restart nova nginx`

**Option B: Main Domain**
1. Go to Cloudflare Dashboard
2. Add Site → Enter domain
3. DNS → Add A record → Your VPS IP → Proxied ✅
4. SSL/TLS → Full mode
5. Done!

**Your Setup:**
```
yourdomain.com          → Existing Cloudflare Worker
api.yourdomain.com      → Nova Backend (this VPS)
```

---

## ✅ Verify It Works

```bash
# Check Nova
systemctl status nova

# Check logs
journalctl -u nova -f

# Test locally
curl http://localhost:8000/

# Test externally
curl http://your-vps-ip/
```

---

## 🎯 Common Issues

**Nova won't start:**
```bash
journalctl -u nova -n 50
# Check Python errors
```

**Ollama not responding:**
```bash
systemctl restart ollama
ollama list
```

**Out of memory:**
```bash
# Add swap
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile && swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

---

## 📊 Resource Usage

**Hostinger KVM 2 (8GB RAM)**: $6.99/mo
- Model: llama3.2:3b
- Response: 10-30s
- Status: ✅ Works fine

**Hostinger KVM 4 (16GB RAM)**: $9.99/mo  
- Model: llama3.2-vision
- Response: 5-20s
- Status: ✅ Better performance

---

## 🔗 Access

- **API**: http://your-vps-ip:8000
- **With Cloudflare**: https://yourdomain.com
- **Discord**: Bot auto-connects
- **Logs**: `journalctl -u nova -f`

---

## 💡 Pro Tips

1. **Monitor resources**: `htop`
2. **Auto-restart**: Already configured in systemd
3. **SSL**: Use Cloudflare (easier) or `certbot`
4. **Backup**: `/opt/nova/backend/chatbot.db`
5. **Updates**: `cd /opt/nova && git pull && systemctl restart nova`

---

## 🆘 Need Help?

See full guide: [HOSTINGER_DEPLOYMENT.md](HOSTINGER_DEPLOYMENT.md)

Nova is now live! 🎉
