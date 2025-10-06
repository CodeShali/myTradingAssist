# 🚀 Quick Start Guide

Get your AI-Assisted Options Trading Platform running in **5 minutes**!

## Prerequisites Check

Before starting, ensure you have:
- ✅ macOS or Linux
- ✅ Python 3.11+ installed
- ✅ Node.js 18+ installed
- ✅ PostgreSQL 15+ installed and running
- ✅ Redis 7+ installed

**Quick Install (macOS)**:
```bash
brew install python node postgresql redis
brew services start postgresql
brew services start redis
```

## Step 1: Get API Keys (5 minutes)

You'll need free API keys from these services:

### 1. Alpaca (Paper Trading - FREE)
1. Go to https://alpaca.markets
2. Sign up for free
3. Navigate to "Paper Trading" → "API Keys"
4. Copy your API Key and Secret Key

### 2. Polygon.io (Market Data - FREE tier available)
1. Go to https://polygon.io
2. Sign up for free tier
3. Copy your API key from dashboard

### 3. NewsAPI (News Data - FREE tier available)
1. Go to https://newsapi.org
2. Sign up for free
3. Copy your API key

### 4. Discord Bot (FREE)
1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Go to "Bot" → "Add Bot"
4. Copy the Bot Token
5. Enable "Message Content Intent" under "Privileged Gateway Intents"
6. Go to OAuth2 → URL Generator
   - Select scope: `bot`
   - Select permissions: Send Messages, Read Messages, Add Reactions
   - Copy and visit the generated URL to invite bot to your server

## Step 2: Configure Environment (2 minutes)

```bash
cd /Users/shashank/Documents/myTradingAssist

# Run the interactive setup wizard
./setup-env.sh
```

The wizard will ask for:
- Your API keys (paste them when prompted)
- Trading mode (choose **paper** for testing)
- PostgreSQL password
- Trading parameters (use defaults for now)

**Important**: Always start with **paper trading mode**!

## Step 3: Start the Platform (1 minute)

```bash
# Start all services
./start.sh
```

This will:
- ✅ Check all prerequisites
- ✅ Validate configuration
- ✅ Create database tables
- ✅ Install dependencies
- ✅ Start all services
- ✅ Run health checks

**Wait for**: "🎉 Platform Started Successfully!"

## Step 4: Access the Platform

Once started, you can access:

- **Web Dashboard**: http://localhost:3001
- **API**: http://localhost:3000
- **Health Check**: http://localhost:3000/health

## Step 5: Create Your Account

### Via Web Dashboard:
1. Open http://localhost:3001
2. Click "Register"
3. Enter username, email, password
4. Click "Create Account"

### Via Command Line:
```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "trader1",
    "email": "trader1@example.com",
    "password": "SecurePassword123!"
  }'
```

## Step 6: Add Symbols to Watch

Add some symbols to start receiving signals:

```bash
# Get your auth token first (from login response)
TOKEN="your_jwt_token_here"

# Add symbols
curl -X POST http://localhost:3000/api/users/watchlist \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "SPY", "notes": "S&P 500 ETF"}'

curl -X POST http://localhost:3000/api/users/watchlist \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "notes": "Apple Inc"}'
```

Or add via web dashboard:
1. Go to "Watchlist" page
2. Click "Add Symbol"
3. Enter symbol (SPY, AAPL, TSLA, etc.)
4. Click "Add"

## Step 7: Wait for Signals

The trading engine generates signals every **5 minutes**. You'll receive notifications via:
- 📱 Discord DM (if bot is configured)
- 🌐 Web Dashboard

## What Happens Next?

### Signal Flow:
1. **AI analyzes** market data every 5 minutes
2. **Signal generated** if opportunity found
3. **You receive notification** via Discord/Web
4. **You confirm** the trade (5-minute window)
5. **Order executes** automatically
6. **Position monitored** in real-time
7. **Auto-exit** at profit target or stop-loss

## Useful Commands

```bash
# Check status
./status.sh

# View logs
./view-logs.sh

# Stop platform
./stop.sh

# Restart platform
./restart.sh
```

## Monitoring Your Trading

### Real-Time Dashboard
- Open http://localhost:3001
- View pending signals
- Monitor open positions
- Check P&L
- Review analytics

### Discord Commands
In Discord, DM your bot:
- `!signals` - View pending signals
- `!positions` - Show open positions
- `!pnl` - Display P&L summary
- `!config` - Show configuration
- `!help` - List all commands

## Troubleshooting

### "Services won't start"
```bash
# Check what's wrong
./status.sh

# View error logs
./view-logs.sh
```

### "No signals generated"
- Wait 5 minutes (signal generation interval)
- Check you have symbols in watchlist
- Check logs: `./view-logs.sh` → Option 2 (Trading Engine)
- Verify API keys are correct in `.env`

### "Database connection failed"
```bash
# Check PostgreSQL is running
pg_isready

# Start PostgreSQL
brew services start postgresql  # macOS
sudo systemctl start postgresql # Linux
```

### "Redis connection failed"
```bash
# Check Redis is running
redis-cli ping

# Start Redis
redis-server --daemonize yes
```

## Configuration Tips

### Adjust Trading Parameters

Edit `.env` file or run `./setup-env.sh` again:

```bash
# Conservative settings (recommended for beginners)
MAX_POSITION_SIZE_PCT=5
MAX_DAILY_TRADES=10
DEFAULT_PROFIT_TARGET_PCT=50
DEFAULT_STOP_LOSS_PCT=50

# Aggressive settings (for experienced traders)
MAX_POSITION_SIZE_PCT=15
MAX_DAILY_TRADES=30
DEFAULT_PROFIT_TARGET_PCT=100
DEFAULT_STOP_LOSS_PCT=30
```

After changes:
```bash
./restart.sh
```

## Safety Checklist

Before going live:

- [ ] Tested in paper trading mode for at least 1 week
- [ ] Reviewed all executed trades
- [ ] Understand profit targets and stop-losses
- [ ] Comfortable with position sizing
- [ ] Reviewed strategy performance
- [ ] Have emergency stop procedures
- [ ] Understand options trading risks

## Next Steps

1. **Test Paper Trading**
   - Let it run for a few days
   - Review signals and executions
   - Adjust parameters as needed

2. **Customize Strategies**
   - Edit `backend/trading_engine/strategies/`
   - Modify risk parameters
   - Add custom filters

3. **Monitor Performance**
   - Review analytics daily
   - Track win rate
   - Analyze strategy effectiveness

4. **Scale Up** (only after thorough testing)
   - Increase position sizes gradually
   - Add more symbols
   - Enable more strategies

## Getting Help

- **Check Status**: `./status.sh`
- **View Logs**: `./view-logs.sh`
- **Documentation**: See `README.md`, `SETUP_GUIDE.md`, `ARCHITECTURE.md`
- **Scripts Help**: See `SCRIPTS_README.md`

## Important Reminders

⚠️ **ALWAYS START IN PAPER TRADING MODE**

⚠️ **Options trading involves substantial risk of loss**

⚠️ **Never trade with money you can't afford to lose**

⚠️ **Past performance does not guarantee future results**

⚠️ **Test thoroughly before using real capital**

---

## Summary

```bash
# Complete setup in 3 commands:
./setup-env.sh    # Configure (one time)
./start.sh        # Start platform
./status.sh       # Verify everything is running
```

Then open http://localhost:3001 and start trading!

**Happy Trading! 🚀📈**
