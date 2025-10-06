# 🤖 Discord Bot Setup Guide

## Complete Step-by-Step Guide

---

## 📋 Overview

Discord integration allows you to:
- ✅ Receive trading signals in Discord
- ✅ Approve/reject trades with emoji reactions
- ✅ Get real-time position updates
- ✅ Receive risk alerts
- ✅ Get daily summaries with NLP (if OpenAI configured)

---

## 🎯 What You Need

1. **Discord Account** (free)
2. **Discord Server** (your own server where bot will post)
3. **5 minutes** to set up

---

## 📝 Step-by-Step Setup

### Step 1: Create Discord Application

1. Go to: https://discord.com/developers/applications
2. Click **"New Application"**
3. Give it a name: `OptionsAI Bot` (or any name you like)
4. Click **"Create"**

### Step 2: Get Application ID & Public Key

1. You're now on the **"General Information"** page
2. Copy these values (you'll need them):
   - **Application ID**: `123456789012345678`
   - **Public Key**: `abc123def456...`

### Step 3: Create Bot

1. Click **"Bot"** in the left sidebar
2. Click **"Add Bot"** → Confirm
3. Under **"Token"**, click **"Reset Token"** → Confirm
4. Copy the **Bot Token**: `MTIzNDU2Nzg5MDEyMzQ1Njc4.GhIjKl.MnOpQrStUvWxYz...`
   - ⚠️ **IMPORTANT**: Save this immediately! You can't see it again.
   - ⚠️ **NEVER share this token publicly!**

### Step 4: Configure Bot Permissions

Still on the Bot page:

1. Scroll down to **"Privileged Gateway Intents"**
2. Enable these:
   - ✅ **MESSAGE CONTENT INTENT** (required!)
   - ✅ **SERVER MEMBERS INTENT** (optional)
   - ✅ **PRESENCE INTENT** (optional)
3. Click **"Save Changes"**

### Step 5: Generate Invite URL

1. Click **"OAuth2"** in the left sidebar
2. Click **"URL Generator"**
3. Select **Scopes**:
   - ✅ `bot`
4. Select **Bot Permissions**:
   - ✅ Send Messages
   - ✅ Send Messages in Threads
   - ✅ Embed Links
   - ✅ Attach Files
   - ✅ Read Message History
   - ✅ Add Reactions
   - ✅ Use External Emojis
5. Copy the **Generated URL** at the bottom

### Step 6: Invite Bot to Your Server

1. Paste the URL from Step 5 into your browser
2. Select your Discord server from the dropdown
3. Click **"Authorize"**
4. Complete the CAPTCHA
5. Bot is now in your server! ✅

### Step 7: Get Server ID

1. Open Discord
2. Go to **Settings** → **Advanced**
3. Enable **"Developer Mode"** ✅
4. Right-click your **server name** (in the left sidebar)
5. Click **"Copy ID"**
6. Save this **Server ID**: `987654321098765432`

### Step 8: Create & Get Channel IDs

You can use one channel for everything, or create separate channels for organization.

#### Option A: Single Channel (Simple)
1. Create one channel: `#optionsai`
2. Right-click the channel → **"Copy ID"**
3. Use this ID for all channel fields

#### Option B: Multiple Channels (Recommended)
1. Create these channels:
   - `#signals` - For AI-generated signals (requires your approval)
   - `#trades` - For trade confirmations
   - `#alerts` - For risk warnings
   - `#updates` - For daily summaries
2. Right-click each channel → **"Copy ID"**
3. Save each ID

---

## 📊 Channel Types Explained

### 1. **Signals Channel** (Most Important!)
**Purpose**: AI posts trading signals here for your approval

**Example Message**:
```
🎯 New Signal: AAPL 150 Call

📊 Confidence: 87% (High)
💰 Entry: $5.50
🎯 Target: $8.25 (+50%)
🛑 Stop: $2.75 (-50%)

💡 Why this trade looks good:
• Technical breakout confirmed
• Earnings beat drove momentum
• News sentiment overwhelmingly bullish

React with ✅ to approve or ❌ to reject
```

**Your Action**: React with ✅ or ❌

### 2. **Trades Channel**
**Purpose**: Confirmation when trades are executed

**Example Message**:
```
✅ Trade Executed: AAPL 150 Call

📈 Filled @ $5.52
📊 Quantity: 9 contracts
💵 Total: $4,974.30

Position is now active and being monitored! 📊
```

### 3. **Alerts Channel**
**Purpose**: Risk warnings and important alerts

**Example Message**:
```
⚠️ Risk Alert: Portfolio Delta Approaching Limit

Current Delta: 85 (Limit: 100)
Action: Consider reducing exposure

Positions contributing most:
• AAPL 150 Call: Delta 45
• TSLA 200 Put: Delta -25
• MSFT 380 Call: Delta 35
```

### 4. **Updates Channel**
**Purpose**: Process updates and daily summaries

**Example Message** (with OpenAI):
```
🌅 Good morning! Starting pre-market analysis...

📊 Market Overview:
S&P 500 futures up 0.3%. VIX at 15.2 suggests
calm conditions - perfect for options strategies.

🔍 Watchlist Analysis:
• AAPL: Strong momentum after earnings beat
• TSLA: High volatility, watching for breakout
• MSFT: Consolidating, waiting for catalyst

🎯 Today's Focus:
Looking for tech sector calls with 30-45 DTE.
IV levels are favorable for entry.

⏰ Market opens in 30 minutes. Let's make it count! 🚀
```

### 5. **Main Channel** (Fallback)
**Purpose**: General notifications if specific channels aren't configured

---

## ⚙️ Configuration Summary

After completing all steps, you'll have:

```env
# From Step 2
DISCORD_APPLICATION_ID=123456789012345678
DISCORD_PUBLIC_KEY=abc123def456...

# From Step 3
DISCORD_BOT_TOKEN=MTIzNDU2Nzg5MDEyMzQ1Njc4.GhIjKl.MnOpQrStUvWxYz...

# From Step 7
DISCORD_GUILD_ID=987654321098765432

# From Step 8
DISCORD_CHANNEL_ID=111111111111111111
DISCORD_SIGNALS_CHANNEL_ID=222222222222222222
DISCORD_TRADES_CHANNEL_ID=333333333333333333
DISCORD_ALERTS_CHANNEL_ID=444444444444444444
DISCORD_UPDATES_CHANNEL_ID=555555555555555555
```

---

## 🚀 Using the Setup Script

When you run `./setup.sh`, you'll see:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. Discord Bot Configuration (Optional)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Discord Setup Steps:
1. Go to: https://discord.com/developers/applications
2. Click 'New Application' → Give it a name
3. Go to 'Bot' section → Click 'Add Bot'
4. Copy the Bot Token
5. Go to 'OAuth2' → 'URL Generator'
   - Select scopes: bot
   - Select permissions: Send Messages, Read Messages, Add Reactions
   - Copy the generated URL and invite bot to your server

To get Channel IDs:
1. In Discord: Settings → Advanced → Enable 'Developer Mode'
2. Right-click any channel → 'Copy ID'

Do you want to configure Discord? (y/n): y

Step 1: Application & Bot Information
─────────────────────────────────────────
Application ID (from General Information page): 123456789012345678
Public Key (from General Information page): abc123def456...
Bot Token (from Bot page): MTIzNDU2Nzg5MDEyMzQ1Njc4.GhIjKl...

Step 2: Server Information
─────────────────────────────────────────
Server ID (right-click server name → Copy ID): 987654321098765432

Step 3: Channel IDs (Optional - press Enter to skip any)
─────────────────────────────────────────

Channel Types:
• Main Channel     - General notifications
• Signals Channel  - AI-generated trading signals (requires your approval)
• Trades Channel   - Trade confirmations and position updates
• Alerts Channel   - Risk alerts and warnings
• Updates Channel  - Process updates and daily summaries

Main Channel ID (general notifications): 111111111111111111
Signals Channel ID (AI signals - recommended!): 222222222222222222
Trades Channel ID (trade confirmations): 333333333333333333
Alerts Channel ID (risk warnings): 444444444444444444
Updates Channel ID (daily summaries): 555555555555555555

✓ Discord configured!
```

---

## ✅ Testing Your Bot

After configuration and starting the platform:

1. Bot should appear **online** in your server
2. You should see a startup message in your main channel:
   ```
   🤖 OptionsAI Bot is now online!
   Ready to send trading signals and updates.
   ```
3. If you don't see this, check:
   - Bot token is correct
   - Bot has permissions in the channels
   - Platform is running (`./status.sh`)

---

## 🔧 Troubleshooting

### Bot Not Appearing Online
- ✅ Check bot token is correct
- ✅ Verify platform is running
- ✅ Check Docker logs: `docker compose logs discord_bot`

### Bot Can't Send Messages
- ✅ Check bot has "Send Messages" permission
- ✅ Verify channel IDs are correct
- ✅ Make sure bot can see the channels

### Reactions Not Working
- ✅ Enable "MESSAGE CONTENT INTENT" in bot settings
- ✅ Check bot has "Add Reactions" permission
- ✅ Verify you're reacting to signal messages

### Getting "Unknown Channel" Error
- ✅ Double-check channel IDs (right-click → Copy ID)
- ✅ Make sure bot is in the server
- ✅ Verify bot can access the channels

---

## 📚 Additional Resources

- **Discord Developer Portal**: https://discord.com/developers/docs
- **Bot Permissions Calculator**: https://discordapi.com/permissions.html
- **Discord.js Guide**: https://discordjs.guide/

---

## 🎯 Quick Reference

### Where to Find Each Value

| Value | Location |
|-------|----------|
| **Application ID** | General Information page |
| **Public Key** | General Information page |
| **Bot Token** | Bot page → Reset Token |
| **Server ID** | Right-click server name → Copy ID |
| **Channel IDs** | Right-click channel → Copy ID |

### Required Permissions

- ✅ Send Messages
- ✅ Read Message History
- ✅ Add Reactions
- ✅ Embed Links

### Required Intents

- ✅ MESSAGE CONTENT INTENT

---

**Your Discord bot is ready to help you trade! 🚀📈**
