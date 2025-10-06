# AI-Assisted Options Trading Platform - Setup Guide

## Quick Start Guide

This guide will help you get the trading platform up and running on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **PostgreSQL 15+** - [Download](https://www.postgresql.org/download/)
- **Redis 7+** - [Download](https://redis.io/download)
- **Git** - [Download](https://git-scm.com/downloads)

## Step 1: Clone and Setup Environment

```bash
cd /Users/shashank/Documents/myTradingAssist

# Copy environment example
cp .env.example .env
```

## Step 2: Configure Environment Variables

Edit the `.env` file with your actual credentials:

```bash
# Required API Keys
ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_key_here
POLYGON_API_KEY=your_polygon_api_key_here
NEWS_API_KEY=your_news_api_key_here
DISCORD_BOT_TOKEN=your_discord_bot_token_here

# Database
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql://trading_user:your_secure_password@localhost:5432/trading_platform

# Security
JWT_SECRET=your_random_32_char_secret_key_here
SESSION_SECRET=your_random_32_char_session_secret_here
```

### Getting API Keys

1. **Alpaca** (Free Paper Trading):
   - Sign up at [alpaca.markets](https://alpaca.markets)
   - Navigate to Paper Trading API keys
   - Copy API Key and Secret Key

2. **Polygon.io** (Market Data):
   - Sign up at [polygon.io](https://polygon.io)
   - Get your API key from dashboard
   - Free tier: 5 requests/minute

3. **NewsAPI** (News Sentiment):
   - Sign up at [newsapi.org](https://newsapi.org)
   - Get your API key
   - Free tier: 1000 requests/day

4. **Discord Bot**:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create New Application
   - Go to Bot section → Add Bot
   - Copy Bot Token
   - Enable Message Content Intent

## Step 3: Database Setup

```bash
# Create PostgreSQL database
createdb trading_platform

# Or using psql
psql -U postgres
CREATE DATABASE trading_platform;
\q

# Run migrations
psql trading_platform < database/migrations/001_initial_schema.sql
```

## Step 4: Install Dependencies

### Python Trading Engine

```bash
cd backend/trading_engine
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Node.js API Gateway

```bash
cd backend/api_gateway
npm install
```

### Discord Bot

```bash
cd backend/discord_bot
npm install
```

### React Frontend

```bash
cd frontend
npm install
```

## Step 5: Start Services

Open 5 separate terminal windows:

### Terminal 1: Redis
```bash
redis-server
```

### Terminal 2: PostgreSQL
```bash
# Usually runs as a service, verify it's running:
pg_isready
```

### Terminal 3: Trading Engine
```bash
cd backend/trading_engine
source venv/bin/activate
python main.py
```

### Terminal 4: API Gateway
```bash
cd backend/api_gateway
npm run dev
```

### Terminal 5: Discord Bot
```bash
cd backend/discord_bot
npm run dev
```

### Terminal 6: Frontend
```bash
cd frontend
npm run dev
```

## Step 6: Access the Platform

- **Web Dashboard**: http://localhost:3001
- **API Gateway**: http://localhost:3000
- **API Health Check**: http://localhost:3000/health

## Step 7: Create Your First User

### Option 1: Via Web Dashboard
1. Navigate to http://localhost:3001
2. Click "Register"
3. Fill in username, email, password
4. Click "Create Account"

### Option 2: Via API
```bash
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "trader1",
    "email": "trader1@example.com",
    "password": "SecurePassword123!"
  }'
```

## Step 8: Link Discord Account

1. Invite your Discord bot to your server:
   - Go to Discord Developer Portal
   - OAuth2 → URL Generator
   - Select `bot` scope
   - Select permissions: Send Messages, Read Messages, Add Reactions
   - Copy and visit the generated URL

2. Link your account:
   - In web dashboard, go to Settings
   - Click "Link Discord Account"
   - Enter your Discord User ID
   - Save

## Step 9: Add Symbols to Watchlist

```bash
# Via API
curl -X POST http://localhost:3000/api/users/watchlist \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "SPY",
    "notes": "S&P 500 ETF"
  }'
```

Or via the web dashboard:
1. Go to Watchlist page
2. Click "Add Symbol"
3. Enter symbol (e.g., SPY, AAPL, TSLA)
4. Click "Add"

## Step 10: Configure Trading Parameters

In the web dashboard:
1. Go to Settings → Trading Configuration
2. Set your preferences:
   - Max Position Size: 10%
   - Max Daily Trades: 20
   - Profit Target: 50%
   - Stop Loss: 50%
   - Enable Auto-Sell: Yes
3. Click "Save Configuration"

## Verification Checklist

- [ ] All services are running without errors
- [ ] Can access web dashboard at http://localhost:3001
- [ ] Can login to web dashboard
- [ ] Discord bot is online in your server
- [ ] Database has tables created
- [ ] Redis is accepting connections
- [ ] Trading engine logs show "Signal generation loop started"
- [ ] API health check returns 200 OK

## Troubleshooting

### Database Connection Errors
```bash
# Check PostgreSQL is running
pg_isready

# Check connection string
psql $DATABASE_URL
```

### Redis Connection Errors
```bash
# Check Redis is running
redis-cli ping
# Should return: PONG
```

### Python Import Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Node.js Module Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Discord Bot Not Responding
- Verify bot token in .env
- Check bot has proper permissions
- Ensure Message Content Intent is enabled
- Check bot is online in Discord

### API Rate Limiting
- Polygon free tier: 5 requests/minute
- NewsAPI free tier: 1000 requests/day
- Consider upgrading plans for production use

## Next Steps

1. **Test Paper Trading**:
   - Ensure TRADING_MODE=paper in .env
   - Add symbols to watchlist
   - Wait for signal generation (runs every 5 minutes)
   - Confirm signals via Discord or web dashboard

2. **Monitor Positions**:
   - View open positions in dashboard
   - Watch real-time P&L updates
   - Test auto-exit at profit targets

3. **Review Analytics**:
   - Check performance metrics
   - Review trade history
   - Analyze strategy performance

4. **Customize Strategies**:
   - Modify strategy parameters in config.py
   - Add custom strategies in strategies/ directory
   - Backtest strategies before going live

## Production Deployment

For production deployment, see:
- [Deployment Guide](docs/deployment/README.md)
- [Security Best Practices](docs/deployment/SECURITY.md)
- [Scaling Guide](docs/deployment/SCALING.md)

## Support

- Check logs in `logs/` directory
- Review error messages in terminal output
- Consult API documentation in `docs/api/`
- Open an issue on GitHub

## Important Reminders

⚠️ **ALWAYS START IN PAPER TRADING MODE**

⚠️ **NEVER commit .env file to version control**

⚠️ **Test thoroughly before using real capital**

⚠️ **Options trading involves substantial risk**

---

**Happy Trading! 🚀📈**
