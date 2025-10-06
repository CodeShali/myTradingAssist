# 🚀 OptionsAI - Complete Setup Guide

## Welcome to Your AI-Assisted Options Trading Platform!

Get up and running in **10 minutes**.

---

## ⚡ Quick Start

### Step 1: Install Docker Desktop
- **Download**: https://www.docker.com/products/docker-desktop
- **Verify**: `docker --version`

### Step 2: Get API Keys (All FREE!)

1. **Alpaca** (Trading): https://alpaca.markets
   - Paper Trading → Generate API Key
   - ⚠️ Use PAPER keys, not LIVE!

2. **Polygon** (Market Data): https://polygon.io
   - Sign up → Copy API key
   - Used for: Options chains, stock quotes, trends

3. **NewsAPI** (Sentiment): https://newsapi.org
   - Sign up → Copy API key

4. **Discord** (Optional): https://discord.com/developers
   - Create bot → Copy token
   - Enable Developer Mode → Copy Channel IDs

5. **OpenAI** (Optional): https://platform.openai.com
   - For enhanced NLP updates (~$0.28-4/month)

### Step 3: Configure

```bash
cd /Users/shashank/Documents/myTradingAssist
./setup.sh
```

Enter your API keys when prompted.

### Step 4: Start

```bash
./start.sh
```

### Step 5: Access

- **Dashboard**: http://localhost:3001
- **API**: http://localhost:3000

---

## 📊 What You Get

### AI-Powered Trading
- Signal generation every 5 minutes
- Multi-factor analysis (technical + sentiment + liquidity)
- Confidence scoring
- Risk assessment

### Multi-Channel Confirmation
- Discord notifications with reactions
- Web dashboard approval
- Manual approval required
- Complete audit trail

### Real-Time Monitoring
- Live P&L tracking
- Position updates
- Market data streaming
- WebSocket connections

### NLP Updates (With OpenAI)
- Pre-market analysis summaries
- Signal explanations
- Position insights
- Daily summaries

---

## 🎯 Platform Features

### Core Features (Always Available)
- ✅ AI signal generation (FinBERT + TA-Lib + ML)
- ✅ Technical analysis (150+ indicators)
- ✅ Sentiment analysis
- ✅ Risk management
- ✅ Position tracking
- ✅ Analytics & charts

### Enhanced Features (With OpenAI)
- ✅ Natural language explanations
- ✅ Conversational Discord updates
- ✅ Market commentary
- ✅ Trading insights

---

## 📚 Documentation

- **[guides/DOCKER_QUICKSTART.md](guides/DOCKER_QUICKSTART.md)** - Docker guide
- **[guides/API_KEYS_GUIDE.md](guides/API_KEYS_GUIDE.md)** - API configuration
- **[guides/CHECKLIST.md](guides/CHECKLIST.md)** - Safety checklist
- **[reference/ARCHITECTURE.md](reference/ARCHITECTURE.md)** - System design

---

## 🎮 Daily Usage

```bash
# Morning
./start.sh

# Check status
./status.sh

# View logs
docker compose logs -f

# Evening
./stop.sh
```

---

## ⚠️ Safety First

### ALWAYS:
- ✅ Start in PAPER mode
- ✅ Test for 1-2 weeks
- ✅ Review all signals
- ✅ Understand risks

### NEVER:
- ❌ Rush to live trading
- ❌ Trade money you can't lose
- ❌ Ignore errors

---

## 🆘 Troubleshooting

```bash
# Check status
./status.sh

# View logs
docker compose logs

# Restart
docker compose restart

# Rebuild
docker compose build --no-cache
```

---

## ✨ You're Ready!

```bash
./setup.sh && ./start.sh
```

**Happy Trading! 🚀📈**

---

## 📚 What to Read Next

### For Docker Users (Recommended):
1. **[DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)** - Complete Docker guide
2. **[CHECKLIST.md](CHECKLIST.md)** - Safety checklist before trading

### For Manual Setup Users:
1. **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Manual installation guide
2. **[CHECKLIST.md](CHECKLIST.md)** - Safety checklist before trading

### For Everyone:
- **[README.md](README.md)** - Platform features and capabilities
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - How it works
- **[INDEX.md](INDEX.md)** - All documentation

---

## 🎯 What You Get

- 🤖 **AI-Powered Signals** - Generated every 5 minutes
- 📱 **Multi-Channel** - Discord + Web confirmations
- 📊 **Real-Time Monitoring** - Live P&L updates
- 💰 **Auto-Exits** - Profit targets & stop-losses
- 📈 **Analytics** - Performance tracking
- 🛡️ **Risk Management** - Portfolio protection

---

## 🆘 Need Help?

### Quick Diagnostics
```bash
./docker-status.sh    # Check if everything is running
docker compose logs -f # View live logs
```

### Common Issues

**Docker not installed?**
- Install Docker Desktop first
- Make sure it's running

**API keys not working?**
- Run `./setup-env.sh` again
- Check `.env` file has your keys

**Containers won't start?**
- Run `docker compose logs` to see errors
- Try `docker compose down && docker compose up -d`

---

## ⚠️ Important Reminders

### ALWAYS:
- ✅ Start in **PAPER TRADING** mode
- ✅ Test for at least 1 week
- ✅ Review all trades
- ✅ Understand the risks

### NEVER:
- ❌ Rush to live trading
- ❌ Trade money you can't afford to lose
- ❌ Ignore error logs
- ❌ Skip the safety checklist

---

## 🎓 Learning Path

### Day 1: Setup
- Install Docker
- Configure API keys
- Start platform
- Create account

### Day 2-7: Paper Trading
- Add symbols to watchlist
- Receive and confirm signals
- Monitor positions
- Review auto-exits

### Week 2: Analysis
- Review performance
- Adjust parameters
- Optimize strategies

### Week 3+: Scale
- Increase position sizes
- Add more symbols
- Fine-tune settings

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| **Start** | `./start.sh` |
| **Stop** | `docker compose down` |
| **Status** | `./docker-status.sh` |
| **Logs** | `docker compose logs -f` |
| **Restart** | `docker compose restart` |

---

## 🎉 You're Ready!

```bash
# One command to start everything:
./start.sh
```

Then open: **http://localhost:3001**

**Happy Trading! 🚀📈**

---

*Questions? Check [INDEX.md](INDEX.md) for all documentation.*
