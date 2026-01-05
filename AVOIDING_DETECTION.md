# 🛡️ Avoiding Discord Bot Detection

Discord has sophisticated bot detection systems. Here's how Nova stays under the radar.

## ⚠️ Important Disclaimer

**This guide is for educational purposes and personal use only.** Using userbots violates Discord's Terms of Service. Account termination is possible. Use at your own risk.

## 🚨 What Triggers Detection

1. **Rapid Actions** - Too many actions too quickly
2. **Perfect Timing** - Actions at exact intervals (robotic)
3. **No Delays** - Instant responses (humans need time to read/type)
4. **Bulk Operations** - Mass friend requests, bulk messages
5. **Suspicious Patterns** - Always online, never idle, instant replies
6. **CAPTCHA Bypass Attempts** - Automated CAPTCHA solving

## ✅ Nova's Anti-Detection Features

### 1. **Human-Like Delays**

```python
# Friend request acceptance: 3-10 seconds
delay = random.uniform(3, 10)

# DM greeting: 5-15 seconds after accepting
dm_delay = random.uniform(5, 15)

# Chat responses: Based on message length
read_time = len(content) * 0.02  # Reading time
think_time = random.uniform(1.0, 3.0)  # Thinking time
typing_delay = random.uniform(0.5, 2.0)  # Before typing
```

### 2. **Variable Timing**

Nova uses `random.uniform()` for all delays:
- ✅ Never the same timing twice
- ✅ Appears human
- ❌ NOT `sleep(5)` every time (robotic)

### 3. **Rate Limiting**

Configure in `nova_config`:
```python
"min_action_delay": 3,  # Minimum 3 seconds
"max_action_delay": 10,  # Maximum 10 seconds
"rate_limit_buffer": 2,  # Extra safety margin
```

### 4. **Realistic Typing Indicators**

Nova shows "typing..." for appropriate durations based on response length.

### 5. **Natural Conversation Patterns**

- Doesn't respond to EVERY message (smart mode)
- Variable response lengths
- Occasional typos/casual language
- Not always available

## 🔧 Configuration Tips

### Adjust Delays (More Conservative)

```python
nova_config = {
    "min_action_delay": 5,   # Increase from 3
    "max_action_delay": 20,  # Increase from 10
    "rate_limit_buffer": 5,  # More safety
}
```

### Limit Auto-Actions

```python
# Disable auto-accept if getting CAPTCHAs
!nova autofriends  # Toggle off

# Manually accept instead
!friends pending
!friends accept <username>
```

### Use Smart Mode

```python
# Don't respond to everything
!nova smart  # AI decides when to respond
!nova mention  # Only when mentioned
```

## 🚫 What NOT To Do

### ❌ Never Automate These:
1. **CAPTCHA Solving** - Will get you banned instantly
2. **Rapid Friending** - Send max 5-10 friend requests per hour
3. **Mass Messaging** - Don't DM 50 people in 5 minutes
4. **Join Spam** - Don't join 20 servers in one session
5. **Perfect Patterns** - Vary your behavior

### ❌ Don't:
- Run 24/7 without breaks
- Respond instantly to everything
- Use the same greeting every time
- Accept ALL friend requests immediately
- Send identical messages repeatedly

## ✅ Best Practices

### 1. **Act Human**
- Take breaks (close Nova for hours)
- Don't be active at 4 AM every night
- Miss some messages occasionally
- Have idle/offline status sometimes

### 2. **Gradual Scaling**
- Start with 1-2 auto-accepts per day
- Gradually increase after weeks
- Never rush

### 3. **Manual CAPTCHA**
When you see a CAPTCHA:
1. **Stop all automation immediately**
2. **Manually complete the CAPTCHA**
3. **Wait 30-60 minutes before resuming**
4. **Reduce automation frequency**

```python
# Emergency: Disable all automation
!nova autofriends  # Turn off auto-accept
!nova autodms      # Turn off auto-DMs
!nova off          # Stop responding
```

### 4. **Monitor Logs**
Watch for warnings:
```
⚠️ Rate limit hit
⚠️ Action failed
⚠️ CAPTCHA required
```

### 5. **Account Age**
- **New accounts** (<1 month) - Very conservative
- **Established accounts** (>6 months) - More leeway
- **Old accounts** (>1 year) - Better trust score

## 📊 Safe Activity Levels

### Conservative (Recommended):
- **Friend Requests**: 5-10 per day
- **DMs**: 20-30 per day
- **Messages**: 100-200 per day
- **Server Joins**: 2-3 per week

### Moderate (Risky):
- **Friend Requests**: 10-20 per day
- **DMs**: 30-50 per day
- **Messages**: 200-300 per day
- **Server Joins**: 5 per week

### Aggressive (Very Risky):
- ❌ **Not recommended**
- High ban risk
- Only for throwaway accounts

## 🆘 If You Get CAPTCHA'd

1. **Stop immediately** - Don't try to automate
2. **Complete manually** - Use your browser/Discord app
3. **Wait** - Give it 1-2 hours
4. **Review settings** - Lower your automation
5. **Gradual restart** - Start very conservatively

```python
# After CAPTCHA, increase delays
nova_config["min_action_delay"] = 10
nova_config["max_action_delay"] = 30
```

## 🔐 Additional Protection

### Use Residential IP
- VPNs can flag you
- Datacenter IPs are suspicious
- Use your home internet

### Realistic User Agent
- discord.py-self handles this
- Don't modify unless needed

### Don't Self-Report
- Don't tell people Nova is a bot
- Maintain character
- Be discreet

## 📈 Nova's Current Settings

Check your settings:
```
!nova status  # View current configuration
!voicestatus  # Voice features
!learn show   # Learning system
```

Current delays (as of now):
- Friend accept: **3-10 seconds** ✅
- Greeting DM: **5-15 seconds** ✅
- Chat response: **1-8 seconds** (based on length) ✅

## 🎯 Summary

**Key Principles:**
1. **Slow is safe** - Longer delays = safer
2. **Random is human** - Never use fixed timings
3. **Less is more** - Fewer actions = less detection
4. **Monitor actively** - Watch for warnings
5. **Manual CAPTCHAs** - Never automate solving

**Remember:** Discord's detection improves constantly. What works today might not work tomorrow. Stay conservative, stay safe.

---

**Questions?**
- Test with `!nova status` to see current settings
- Adjust `nova_config` in `discord_bot.py` as needed
- Monitor console logs for warnings
- When in doubt, go slower and more manual
