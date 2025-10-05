# 🚀 START HERE - Quick Setup Guide

## Welcome to Your AI-Assisted Options Trading Platform!

This guide will get you trading in **under 10 minutes**.

---

## ⚡ Super Quick Start (Recommended)

### Step 1: Install Docker Desktop (5 minutes)

**Download and install:**
- **macOS/Windows**: https://www.docker.com/products/docker-desktop
- **Linux**: `curl -fsSL https://get.docker.com | sh`

**Verify installation:**
```bash
docker --version
docker compose version
```

### Step 2: Get API Keys (5 minutes)

You need FREE API keys from:

1. **Alpaca** (Paper Trading): https://alpaca.markets
   - Sign up → Paper Trading → API Keys

2. **Polygon.io** (Market Data): https://polygon.io
   - Sign up → Copy API key

3. **NewsAPI** (News): https://newsapi.org
   - Sign up → Copy API key

4. **Discord Bot** (Optional): https://discord.com/developers/applications
   - Create app → Bot → Copy token

### Step 3: Configure & Start (2 minutes)

```bash
cd /Users/shashank/Documents/myTradingAssist

# Configure your API keys
./setup-env.sh

# Start everything!
./start.sh
```

### Step 4: Access Your Platform

- **Web Dashboard**: http://localhost:3001
- **API**: http://localhost:3000

**That's it! You're trading! 🎉**

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
