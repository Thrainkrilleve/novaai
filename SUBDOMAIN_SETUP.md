# 🌐 Subdomain Setup for Nova (Cloudflare + Existing Worker)

## Scenario

You already have:
- ✅ `yourdomain.com` → Cloudflare Worker
- ✅ Ubuntu VPS with Nova installed
- ⏳ Want Nova on a subdomain

## Solution: Use Subdomain

```
yourdomain.com          → Your existing Worker (unchanged)
api.yourdomain.com      → Nova Backend on VPS
```

---

## 🚀 Quick Setup (5 minutes)

### 1. Add DNS Record in Cloudflare

Go to Cloudflare Dashboard → Your Domain → DNS

**Add A Record:**
```
Type: A
Name: api
Content: YOUR_VPS_IP_ADDRESS
Proxy: ✅ Proxied (orange cloud)
TTL: Auto
```

**Result:** Creates `api.yourdomain.com`

**Other good subdomain names:**
- `nova.yourdomain.com`
- `bot.yourdomain.com`
- `ai.yourdomain.com`

---

### 2. Update Nginx on VPS

SSH to your VPS:
```bash
ssh root@your-vps-ip
```

Edit Nginx config:
```bash
sudo nano /etc/nginx/sites-available/nova
```

Change `server_name` line:
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;  # ← Change this
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_cache_bypass $http_upgrade;
    }
}
```

Test and restart:
```bash
sudo nginx -t
sudo systemctl restart nginx
```

---

### 3. Update Nova Configuration

Edit `.env`:
```bash
cd /opt/nova/backend
nano .env
```

Update:
```env
HOST=0.0.0.0
PORT=8000

# Your subdomain
DOMAIN=api.yourdomain.com

# If you have frontend on another subdomain
FRONTEND_URL=https://app.yourdomain.com
```

Restart Nova:
```bash
sudo systemctl restart nova
```

---

### 4. SSL/TLS Configuration

In Cloudflare Dashboard → SSL/TLS → Overview:

**Set encryption mode:**
- **Full** (recommended) - Requires HTTPS between Cloudflare and your VPS
- **Flexible** - HTTP between Cloudflare and VPS (less secure)

**If using Full mode, install certificate on VPS:**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d api.yourdomain.com
```

**Enable additional SSL settings:**
1. SSL/TLS → Edge Certificates
2. Enable:
   - ✅ Always Use HTTPS
   - ✅ Automatic HTTPS Rewrites
   - ✅ Minimum TLS Version: 1.2

---

## ✅ Verify It Works

### Test DNS Resolution
```bash
# From your computer
nslookup api.yourdomain.com
# Should show Cloudflare IPs
```

### Test HTTP Access
```bash
curl http://api.yourdomain.com/
# Should return Nova response
```

### Test HTTPS Access
```bash
curl https://api.yourdomain.com/
# Should return Nova response
```

### Check Logs on VPS
```bash
sudo journalctl -u nova -f
```

---

## 🏗️ Complete Architecture

```
┌────────────────────────────────────────┐
│         Cloudflare (Edge)              │
│  ┌──────────────────────────────────┐  │
│  │  yourdomain.com → Worker         │  │
│  │  api.yourdomain.com → Proxy      │  │
│  └──────────────────────────────────┘  │
│    SSL/TLS, DDoS Protection, CDN       │
└────────────────────────────────────────┘
                    ↓
┌────────────────────────────────────────┐
│         Your VPS (Ubuntu)              │
│  ┌──────────────────────────────────┐  │
│  │  Nginx (Reverse Proxy)           │  │
│  │  ├─ api.yourdomain.com:80/443   │  │
│  │  └─ Forwards to → :8000          │  │
│  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────┐  │
│  │  Nova Backend (:8000)            │  │
│  │  ├─ FastAPI                      │  │
│  │  ├─ Discord Bot                  │  │
│  │  └─ Ollama LLM                   │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘
```

---

## 📊 What You Get

### ✅ Benefits of Subdomain Setup

1. **No Conflicts** - Worker and Nova run independently
2. **Clean Separation** - Different services on different subdomains
3. **Cloudflare Protection** - Both get DDoS protection and SSL
4. **Flexible** - Easy to add more subdomains later
5. **Professional** - Clean URL structure

### 🌐 Example Multi-Service Setup

```
yourdomain.com              → Main website/Worker
api.yourdomain.com          → Nova Backend API
app.yourdomain.com          → Nova Frontend (Cloudflare Pages)
cdn.yourdomain.com          → Static assets (R2)
status.yourdomain.com       → Status page
```

---

## 🔧 Troubleshooting

### DNS Not Resolving
```bash
# Wait 5-10 minutes for DNS propagation
# Check DNS
dig api.yourdomain.com
nslookup api.yourdomain.com
```

### 502 Bad Gateway
```bash
# Check Nova is running
sudo systemctl status nova

# Check Nginx
sudo systemctl status nginx
sudo nginx -t

# Check logs
sudo journalctl -u nova -n 50
```

### SSL Certificate Issues
```bash
# If using certbot
sudo certbot renew --dry-run

# Check Cloudflare SSL mode
# Should be "Full" or "Full (strict)"
```

### CORS Errors
Nova's CORS is configured in `main.py`. The Cloudflare middleware will handle proxy headers automatically.

---

## 🎉 Success!

Your setup:
- ✅ `yourdomain.com` → Your existing Worker (unchanged)
- ✅ `api.yourdomain.com` → Nova AI (on VPS)
- ✅ Both protected by Cloudflare
- ✅ SSL/TLS enabled
- ✅ DDoS protection active

**Access Nova:**
- API: `https://api.yourdomain.com/`
- WebSocket: `wss://api.yourdomain.com/ws`
- Health: `https://api.yourdomain.com/health`

**Test Discord Bot:**
Your Discord bot will use the subdomain automatically based on your `.env` configuration.

---

## 💡 Optional: Add Frontend

If you want a web UI:

1. Deploy frontend to Cloudflare Pages
2. Create subdomain: `app.yourdomain.com`
3. Update `.env`:
   ```env
   FRONTEND_URL=https://app.yourdomain.com
   ```
4. Configure CORS in `main.py` (already done)

Your complete setup:
```
yourdomain.com          → Worker
api.yourdomain.com      → Backend (VPS)
app.yourdomain.com      → Frontend (Pages)
```

Perfect multi-service architecture! 🚀
