# 🔧 OptionsAI Configuration - Complete Guide

## Your Questions Answered

---

## 1️⃣ **Alpaca API URLs**

### ✅ **Correct URLs**

You're absolutely right! The platform now uses the correct endpoints:

**Paper Trading:**
```
https://paper-api.alpaca.markets/v2
```

**Live Trading:**
```
https://api.alpaca.markets/v2
```

### Configuration

In your `.env` file:
```env
# For Paper Trading (recommended)
ALPACA_API_KEY=your_paper_api_key
ALPACA_SECRET_KEY=your_paper_secret_key
ALPACA_BASE_URL=https://paper-api.alpaca.markets/v2
TRADING_MODE=paper

# For Live Trading (after testing!)
ALPACA_API_KEY=your_live_api_key
ALPACA_SECRET_KEY=your_live_secret_key
ALPACA_BASE_URL=https://api.alpaca.markets/v2
TRADING_MODE=live
```

### How It Works

The platform uses Alpaca for:
- ✅ **Order execution** - Buying/selling options
- ✅ **Position management** - Tracking open positions
- ✅ **Account data** - Balance, buying power
- ✅ **Order status** - Filled, pending, rejected

---

## 2️⃣ **Polygon.io API Usage**

### ✅ **Yes! Polygon is for Market Data**

Polygon.io provides:

1. **Options Chain Data**
   - All available strikes
   - Expiration dates
   - Bid/ask prices
   - Open interest
   - Volume

2. **Stock Data & Trends**
   - Real-time quotes
   - Historical prices (OHLCV)
   - Intraday data
   - After-hours trading

3. **Technical Indicators**
   - Moving averages
   - RSI, MACD
   - Bollinger Bands
   - Volume indicators

4. **Greeks**
   - Delta, Gamma, Theta, Vega
   - Implied volatility
   - Option pricing data

### Example Usage in Platform

```python
# Get options chain
polygon.get_options_chain('AAPL', expiration='2025-01-17')

# Get stock quote
polygon.get_quote('AAPL')

# Get historical data for technical analysis
polygon.get_historical('AAPL', timeframe='1D', limit=100)
```

---

## 3️⃣ **Discord Channel ID & Process**

### ✅ **Channel ID Support Added!**

You can now configure multiple channels for different notifications:

```env
# Main Discord Configuration
DISCORD_BOT_TOKEN=your_bot_token
DISCORD_GUILD_ID=your_server_id
DISCORD_ADMIN_USER_ID=your_user_id

# Channel IDs for different notification types
DISCORD_CHANNEL_ID=123456789  # Main channel
DISCORD_SIGNALS_CHANNEL_ID=987654321  # AI signals
DISCORD_TRADES_CHANNEL_ID=111222333  # Trade confirmations
DISCORD_ALERTS_CHANNEL_ID=444555666  # Alerts & warnings
DISCORD_UPDATES_CHANNEL_ID=777888999  # Process updates
```

### How Discord Process Works

#### **1. Bot Setup**
```
1. Create bot at: https://discord.com/developers/applications
2. Enable "Message Content Intent"
3. Invite bot to your server with permissions:
   - Send Messages
   - Embed Links
   - Read Message History
   - Add Reactions
4. Copy bot token and channel IDs
```

#### **2. Signal Flow**
```
AI Engine → Generates Signal → Discord Bot → Posts to SIGNALS channel
                                              ↓
User sees signal → Reacts with ✅ or ❌ → Bot captures reaction
                                              ↓
                                    Executes trade or rejects
```

#### **3. Notification Types**

**Signals Channel:**
```
🎯 New Signal: AAPL 150 Call
📊 Confidence: 85%
💰 Entry: $5.50
🎯 Target: $8.25 (+50%)
🛑 Stop: $2.75 (-50%)
React with ✅ to approve or ❌ to reject
```

**Trades Channel:**
```
✅ Trade Executed: AAPL 150 Call
📈 Filled @ $5.52
📊 Quantity: 5 contracts
💵 Total: $2,760
```

**Updates Channel:**
```
🌅 Pre-market analysis started
📊 Scanning 50 symbols...
🎯 3 signals generated
⏰ Market opens in 15 minutes
```

---

## 4️⃣ **NLP-Based Discord Updates**

### ✅ **Enhanced with OpenAI Integration**

The platform now supports OpenAI API for natural language updates!

### Configuration

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo
```

### NLP Update Examples

#### **Pre-Market Updates**
```
🌅 Good morning! Starting pre-market analysis...

📊 Market Overview:
• S&P 500 futures up 0.3%
• VIX at 15.2 (low volatility)
• Pre-market volume: moderate

🔍 Scanning watchlist:
• AAPL: Bullish momentum, testing resistance
• TSLA: High IV, potential breakout
• MSFT: Consolidating, waiting for catalyst

🎯 Strategy for today:
Focus on tech sector calls with 30-45 DTE.
Looking for IV rank < 50 for better entry prices.

⏰ Market opens in 30 minutes. Stay tuned!
```

#### **Signal Generation Updates**
```
🤖 AI Analysis Complete

📈 Bullish Signals Found: 3
• AAPL 150 Call - High confidence (87%)
• MSFT 380 Call - Medium confidence (72%)
• GOOGL 140 Call - Medium confidence (68%)

📉 Bearish Signals: 1
• TSLA 200 Put - Low confidence (55%)

💡 Recommendation:
AAPL signal looks strongest with:
✓ Positive earnings momentum
✓ Technical breakout confirmed
✓ High liquidity (tight spreads)
✓ Favorable risk/reward ratio

Waiting for your approval...
```

#### **Position Updates**
```
📊 Position Update: AAPL 150 Call

Current Status:
• Entry: $5.50
• Current: $7.25 (+31.8%)
• Target: $8.25 (13.8% away)
• Stop: $2.75 (162% buffer)

Greeks:
• Delta: 0.65 (in-the-money)
• Theta: -0.08 (time decay manageable)
• IV: 28% (stable)

💡 Analysis:
Position is performing well. Approaching profit target.
Consider taking partial profits at $8.00.
```

#### **End-of-Day Summary**
```
📊 Daily Trading Summary

Performance:
• Trades: 5 executed
• Winners: 4 (80% win rate)
• P&L: +$1,245 (+4.2%)
• Best trade: AAPL 150 Call (+$625)

Key Insights:
✓ Tech sector calls performed well
✓ Early entries captured momentum
✓ Stop losses protected 1 losing trade

Tomorrow's Plan:
• Watch for Fed announcement at 2pm
• Focus on defensive sectors if volatility spikes
• Keep position sizes conservative

Great day! See you tomorrow 🚀
```

### How to Enable NLP Updates

1. **Add OpenAI API Key** to `.env`
2. **Configure Update Channel**:
   ```env
   DISCORD_UPDATES_CHANNEL_ID=your_channel_id
   ```
3. **Set Update Frequency** in backend config
4. **Customize Messages** in `backend/discord_bot/nlp_updates.js`

---

## 5️⃣ **AI & Machine Learning**

### Current AI Stack (No OpenAI Required!)

The platform uses **built-in AI models** that don't require OpenAI:

#### **1. FinBERT (Financial Sentiment Analysis)**
```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Analyzes news headlines
model = "ProsusAI/finbert"
# Returns: positive, negative, neutral sentiment
```

#### **2. Technical Analysis (TA-Lib)**
```python
import talib

# RSI, MACD, Bollinger Bands, etc.
rsi = talib.RSI(prices, timeperiod=14)
macd = talib.MACD(prices)
```

#### **3. Scikit-Learn (Pattern Recognition)**
```python
from sklearn.ensemble import RandomForestClassifier

# Predicts price movements based on historical patterns
model.fit(features, labels)
```

#### **4. Custom Scoring Algorithm**
```python
# Multi-factor scoring system
score = (
    technical_score * 0.3 +
    sentiment_score * 0.2 +
    liquidity_score * 0.2 +
    greeks_score * 0.3
)
```

### OpenAI Integration (Optional Enhancement)

**When you add OpenAI API key**, you get:

1. **Enhanced News Analysis**
   - Deeper sentiment understanding
   - Context-aware analysis
   - Multi-article synthesis

2. **Natural Language Updates**
   - Human-like Discord messages
   - Personalized insights
   - Conversational responses

3. **Strategy Suggestions**
   - AI-powered trade ideas
   - Risk assessment explanations
   - Market commentary

4. **Query System**
   - Ask questions about positions
   - Get explanations of signals
   - Understand market conditions

### Example: With vs Without OpenAI

**Without OpenAI (Built-in AI):**
```
Signal: AAPL 150 Call
Confidence: 85%
RSI: 65 (bullish)
Sentiment: Positive
```

**With OpenAI (Enhanced):**
```
🎯 AAPL 150 Call Signal

Why this trade looks good:
Apple is showing strong momentum after beating earnings expectations.
The RSI at 65 indicates bullish momentum without being overbought.
News sentiment is overwhelmingly positive, with analysts raising
price targets. The 150 strike offers good delta exposure while
keeping premium costs reasonable.

Risk factors to consider:
• Broader market volatility could impact tech stocks
• Earnings run-up may lead to IV crush
• Consider taking profits before next Fed meeting

Confidence: 85% (High)
```

---

## 🔧 **Complete Configuration Example**

Here's your `.env` file with everything configured:

```env
# Alpaca Trading (Paper Mode)
ALPACA_API_KEY=PK1234567890ABCDEF
ALPACA_SECRET_KEY=abcdef1234567890xyz
ALPACA_BASE_URL=https://paper-api.alpaca.markets/v2
TRADING_MODE=paper

# Polygon Market Data
POLYGON_API_KEY=your_polygon_key_here

# NewsAPI
NEWS_API_KEY=your_newsapi_key_here

# OpenAI (Optional - for enhanced NLP)
OPENAI_API_KEY=sk-proj-abc123xyz
OPENAI_MODEL=gpt-4

# Discord Configuration
DISCORD_BOT_TOKEN=your_bot_token
DISCORD_GUILD_ID=123456789012345678
DISCORD_ADMIN_USER_ID=987654321098765432

# Discord Channels
DISCORD_CHANNEL_ID=111111111111111111
DISCORD_SIGNALS_CHANNEL_ID=222222222222222222
DISCORD_TRADES_CHANNEL_ID=333333333333333333
DISCORD_ALERTS_CHANNEL_ID=444444444444444444
DISCORD_UPDATES_CHANNEL_ID=555555555555555555

# Database
POSTGRES_PASSWORD=secure_password_here
DATABASE_URL=postgresql://trading_user:secure_password_here@postgres:5432/trading_platform

# Redis
REDIS_URL=redis://redis:6379

# Security
JWT_SECRET=your_very_long_random_jwt_secret_key_here_min_32_chars
SESSION_SECRET=your_session_secret_key_here

# Trading Configuration
MAX_POSITION_SIZE_PCT=10
MAX_DAILY_TRADES=20
DEFAULT_PROFIT_TARGET_PCT=50
DEFAULT_STOP_LOSS_PCT=50
```

---

## 🚀 **Next Steps**

1. **Update your `.env` file** with the correct values
2. **Get Discord Channel IDs**:
   - Enable Developer Mode in Discord
   - Right-click channel → Copy ID
3. **Optional: Add OpenAI API key** for enhanced NLP
4. **Start the platform**: `./start.sh`

---

## 📚 **Additional Resources**

- **Alpaca API Docs**: https://alpaca.markets/docs/api-references/
- **Polygon API Docs**: https://polygon.io/docs/
- **Discord Bot Guide**: https://discord.com/developers/docs/
- **OpenAI API**: https://platform.openai.com/docs/

---

**Your platform is now configured for maximum functionality! 🚀📈**
