# 🔄 Backend Workflow - Complete Lifecycle

## Overview

This document explains **exactly what happens** in the backend from the moment you start the platform until a trade is executed and closed.

---

## 🎯 Table of Contents

1. [System Startup](#1-system-startup)
2. [Signal Generation Lifecycle](#2-signal-generation-lifecycle)
3. [Trade Execution Flow](#3-trade-execution-flow)
4. [Position Management](#4-position-management)
5. [Risk Management](#5-risk-management)
6. [Discord Integration](#6-discord-integration)
7. [Data Flow](#7-data-flow)

---

## 1. System Startup

### What Happens When You Run `./start.sh`

```
┌─────────────────────────────────────────────────────────────┐
│                    SYSTEM STARTUP FLOW                      │
└─────────────────────────────────────────────────────────────┘

User runs: ./start.sh
     ↓
Docker Compose starts 6 containers:
     ↓
┌────────────────────────────────────────────────────────────┐
│  1. PostgreSQL    → Database starts, loads schema          │
│  2. Redis         → Cache starts, connects                 │
│  3. Trading Engine → Python service initializes            │
│  4. API Gateway   → Node.js server starts                  │
│  5. Discord Bot   → Connects to Discord                    │
│  6. Frontend      → React app builds & serves              │
└────────────────────────────────────────────────────────────┘
     ↓
Each service performs initialization:
     ↓
┌─────────────────────────────────────────────────────────────┐
│ TRADING ENGINE (Python)                                     │
│ ─────────────────────────────────────────────────────────── │
│ 1. Load configuration from .env                             │
│ 2. Connect to PostgreSQL database                           │
│ 3. Connect to Redis cache                                   │
│ 4. Initialize API clients:                                  │
│    - Alpaca API (trading)                                   │
│    - Polygon API (market data)                              │
│    - NewsAPI (sentiment)                                    │
│    - OpenAI API (optional, NLP)                             │
│ 5. Load AI models:                                          │
│    - FinBERT (sentiment analysis)                           │
│    - Technical indicators (TA-Lib)                          │
│    - ML models (Scikit-Learn)                               │
│ 6. Start background tasks:                                  │
│    - Signal generation (every 5 min)                        │
│    - Position monitoring (every 3 sec)                      │
│    - Risk checks (every 30 sec)                             │
│    - Market data updates (real-time)                        │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ API GATEWAY (Node.js)                                       │
│ ─────────────────────────────────────────────────────────── │
│ 1. Start Express server on port 3000                        │
│ 2. Connect to PostgreSQL                                    │
│ 3. Connect to Redis                                         │
│ 4. Initialize WebSocket server                              │
│ 5. Set up REST API routes:                                  │
│    - /api/auth/* (authentication)                           │
│    - /api/signals/* (signals management)                    │
│    - /api/positions/* (positions tracking)                  │
│    - /api/analytics/* (performance data)                    │
│    - /api/watchlist/* (symbols)                             │
│ 6. Start listening for events from Trading Engine           │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ DISCORD BOT (Node.js)                                       │
│ ─────────────────────────────────────────────────────────── │
│ 1. Connect to Discord API                                   │
│ 2. Join configured server (guild)                           │
│ 3. Verify channel access                                    │
│ 4. Initialize OpenAI client (if configured)                 │
│ 5. Set up event listeners:                                  │
│    - Message reactions (for signal approval)                │
│    - Commands (admin controls)                              │
│ 6. Subscribe to Trading Engine events                       │
│ 7. Send startup notification to Discord                     │
└─────────────────────────────────────────────────────────────┘
     ↓
System Ready! ✅
```

---

## 2. Signal Generation Lifecycle

### Complete Flow: From Market Data to Signal

```
┌─────────────────────────────────────────────────────────────┐
│              SIGNAL GENERATION LIFECYCLE                    │
│                  (Every 5 Minutes)                          │
└─────────────────────────────────────────────────────────────┘

TIMER TRIGGERS (every 5 minutes)
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: FETCH WATCHLIST                                     │
│ ─────────────────────────────────────────────────────────── │
│ Query: SELECT * FROM watchlist WHERE active = true          │
│ Result: ['AAPL', 'TSLA', 'MSFT', 'GOOGL', ...]            │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: FETCH MARKET DATA (Parallel for each symbol)       │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ For AAPL:                                                   │
│   ┌─────────────────────────────────────────────────────┐ │
│   │ A. Stock Data (Polygon API)                         │ │
│   │    - Current price: $150.25                         │ │
│   │    - Volume: 45.2M                                  │ │
│   │    - Historical prices (30 days)                    │ │
│   │    - After-hours data                               │ │
│   └─────────────────────────────────────────────────────┘ │
│                ↓                                            │
│   ┌─────────────────────────────────────────────────────┐ │
│   │ B. Options Chain (Polygon API)                      │ │
│   │    - All strikes for next 4 expirations             │ │
│   │    - Bid/ask prices                                 │ │
│   │    - Open interest                                  │ │
│   │    - Volume                                         │ │
│   │    - Greeks (Delta, Gamma, Theta, Vega)            │ │
│   │    - Implied Volatility                             │ │
│   └─────────────────────────────────────────────────────┘ │
│                ↓                                            │
│   ┌─────────────────────────────────────────────────────┐ │
│   │ C. News Headlines (NewsAPI)                         │ │
│   │    - Last 24 hours of news                          │ │
│   │    - "Apple beats earnings expectations"            │ │
│   │    - "Apple announces new product line"             │ │
│   │    - "Analysts raise AAPL price target"             │ │
│   └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: TECHNICAL ANALYSIS                                  │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ Using TA-Lib on historical price data:                      │
│                                                             │
│ RSI (Relative Strength Index):                             │
│   rsi = talib.RSI(prices, timeperiod=14)                   │
│   → Result: 65 (Bullish, not overbought)                   │
│                                                             │
│ MACD (Moving Average Convergence Divergence):               │
│   macd, signal, hist = talib.MACD(prices)                  │
│   → Result: Bullish crossover detected                     │
│                                                             │
│ Bollinger Bands:                                            │
│   upper, middle, lower = talib.BBANDS(prices)              │
│   → Result: Price near upper band (bullish)                │
│                                                             │
│ Moving Averages:                                            │
│   ma_20 = talib.SMA(prices, 20)                            │
│   ma_50 = talib.SMA(prices, 50)                            │
│   → Result: 20-day > 50-day (golden cross)                 │
│                                                             │
│ Volume Analysis:                                            │
│   → Result: Above average volume (confirmation)            │
│                                                             │
│ TECHNICAL SCORE: 8.5/10 ✅                                  │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: SENTIMENT ANALYSIS                                  │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ Using FinBERT (Financial BERT) on news headlines:           │
│                                                             │
│ Headline 1: "Apple beats earnings expectations"             │
│   → Sentiment: POSITIVE (0.92 confidence)                  │
│                                                             │
│ Headline 2: "Apple announces new product line"              │
│   → Sentiment: POSITIVE (0.88 confidence)                  │
│                                                             │
│ Headline 3: "Analysts raise AAPL price target"              │
│   → Sentiment: POSITIVE (0.95 confidence)                  │
│                                                             │
│ Aggregate Sentiment:                                        │
│   - Positive: 85%                                           │
│   - Neutral: 10%                                            │
│   - Negative: 5%                                            │
│                                                             │
│ SENTIMENT SCORE: 9.0/10 ✅                                  │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: OPTIONS ANALYSIS                                    │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ Find optimal strike and expiration:                         │
│                                                             │
│ Criteria:                                                   │
│   - Delta: 0.50 - 0.70 (good leverage)                     │
│   - Liquidity: Open interest > 100                         │
│   - Spread: Bid-ask spread < 5%                            │
│   - DTE: 30-45 days (sweet spot)                           │
│   - IV Rank: < 50 (not overpriced)                         │
│                                                             │
│ Best Option Found:                                          │
│   Symbol: AAPL 150 Call                                    │
│   Expiration: 2025-02-21 (45 DTE)                          │
│   Strike: $150                                              │
│   Premium: $5.50                                            │
│   Delta: 0.55                                               │
│   Theta: -0.08                                              │
│   IV: 28%                                                   │
│   Open Interest: 5,420                                      │
│   Bid-Ask Spread: 2.1% ✅                                   │
│                                                             │
│ LIQUIDITY SCORE: 9.5/10 ✅                                  │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: RISK ASSESSMENT                                     │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ Check portfolio constraints:                                │
│                                                             │
│ ✅ Position size: $2,750 (< 10% of portfolio)              │
│ ✅ Daily trades: 3 today (< 20 limit)                      │
│ ✅ Portfolio delta: 45 (< 100 limit)                       │
│ ✅ Concentration: 15% in tech (< 25% limit)                │
│ ✅ Buying power: $25,000 available                         │
│ ✅ Pattern day trading: Compliant                          │
│                                                             │
│ Calculate stop-loss and profit target:                      │
│   Entry: $5.50                                              │
│   Stop-loss: $2.75 (-50%)                                  │
│   Profit target: $8.25 (+50%)                              │
│   Risk/Reward: 1:1 ✅                                       │
│                                                             │
│ RISK SCORE: 8.0/10 ✅                                       │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 7: MULTI-FACTOR SCORING                               │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ Weighted Score Calculation:                                 │
│                                                             │
│   Technical Score:  8.5 × 0.30 = 2.55                      │
│   Sentiment Score:  9.0 × 0.20 = 1.80                      │
│   Liquidity Score:  9.5 × 0.20 = 1.90                      │
│   Risk Score:       8.0 × 0.30 = 2.40                      │
│                          ─────────                          │
│   TOTAL CONFIDENCE:      8.65/10 = 87%                     │
│                                                             │
│ Decision: GENERATE SIGNAL ✅                                │
│ (Threshold: 80% confidence)                                 │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 8: GENERATE SIGNAL WITH OPENAI (Optional)             │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ If OpenAI is configured, generate explanation:              │
│                                                             │
│ Prompt to GPT-4:                                            │
│   "Explain this signal: AAPL 150 Call, 87% confidence      │
│    Technical: RSI 65, MACD bullish, price at upper BB      │
│    Sentiment: 85% positive from earnings beat               │
│    Why is this a good trade?"                               │
│                                                             │
│ GPT-4 Response:                                             │
│   "This AAPL 150 Call looks strong because:                │
│    • Technical breakout confirmed above $148 resistance     │
│    • Earnings beat drove positive momentum                 │
│    • News sentiment overwhelmingly bullish                 │
│    • Excellent liquidity with tight spreads                │
│                                                             │
│    Risk factors to consider:                                │
│    • Broader market volatility could impact tech           │
│    • IV may crush after earnings run-up                    │
│    • Consider taking profits before Fed meeting            │
│                                                             │
│    Overall: High-confidence setup with good risk/reward"   │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 9: SAVE TO DATABASE                                    │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ INSERT INTO signals (                                       │
│   symbol, type, strike, expiration,                         │
│   entry_price, stop_loss, profit_target,                    │
│   confidence, technical_score, sentiment_score,             │
│   liquidity_score, risk_score,                              │
│   explanation, status, created_at                           │
│ ) VALUES (                                                  │
│   'AAPL', 'call', 150, '2025-02-21',                       │
│   5.50, 2.75, 8.25,                                        │
│   0.87, 0.85, 0.90, 0.95, 0.80,                            │
│   '[OpenAI explanation]', 'pending', NOW()                  │
│ )                                                           │
│                                                             │
│ Signal ID: 12345 ✅                                         │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 10: NOTIFY USERS                                       │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ A. Publish to Redis (for real-time updates):                │
│    PUBLISH signal:new {signal_data}                         │
│                                                             │
│ B. Send to API Gateway via WebSocket:                       │
│    → API Gateway broadcasts to connected web clients        │
│                                                             │
│ C. Send to Discord Bot:                                     │
│    → Discord posts to SIGNALS channel                       │
│    → Adds reaction buttons (✅ ❌)                          │
│                                                             │
│ D. Store in cache for quick access:                         │
│    SET signal:12345 {signal_data} EX 300                   │
└─────────────────────────────────────────────────────────────┘
     ↓
Signal Generated! Waiting for user approval...
```

---

## 3. Trade Execution Flow

### What Happens When You Approve a Signal

```
┌─────────────────────────────────────────────────────────────┐
│              TRADE EXECUTION FLOW                           │
└─────────────────────────────────────────────────────────────┘

USER APPROVES SIGNAL (via Discord ✅ or Web Dashboard)
     ↓
┌─────────────────────────────────────────────────────────────┐
│ DISCORD BOT / API GATEWAY                                   │
│ ─────────────────────────────────────────────────────────── │
│ 1. Capture approval event                                   │
│ 2. Verify user authorization                                │
│ 3. Check signal is still valid (not expired)                │
│ 4. Send approval to Trading Engine                          │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ TRADING ENGINE: PRE-EXECUTION CHECKS                        │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ 1. Verify signal exists and is pending                      │
│    SELECT * FROM signals WHERE id = 12345                   │
│    AND status = 'pending'                                   │
│                                                             │
│ 2. Check market hours                                       │
│    if not market_open():                                    │
│        return "Market closed"                               │
│                                                             │
│ 3. Re-check current price                                   │
│    current_price = polygon.get_quote('AAPL 150 Call')      │
│    if abs(current_price - signal.entry_price) > 10%:       │
│        return "Price moved too much"                        │
│                                                             │
│ 4. Verify buying power                                      │
│    account = alpaca.get_account()                           │
│    if account.buying_power < required_capital:              │
│        return "Insufficient buying power"                   │
│                                                             │
│ 5. Check position limits                                    │
│    if current_positions >= MAX_DAILY_TRADES:                │
│        return "Daily trade limit reached"                   │
│                                                             │
│ All checks passed ✅                                        │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: CALCULATE POSITION SIZE                             │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ Portfolio value: $50,000                                    │
│ Max position size: 10% = $5,000                             │
│ Option price: $5.50 per contract                            │
│ Contract multiplier: 100                                    │
│ Cost per contract: $5.50 × 100 = $550                       │
│                                                             │
│ Max contracts: $5,000 / $550 = 9.09                         │
│ Round down: 9 contracts                                     │
│ Total cost: 9 × $550 = $4,950                               │
│                                                             │
│ Position size: 9 contracts ✅                               │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: PLACE ORDER WITH ALPACA                             │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ order = alpaca.submit_order(                                │
│     symbol='AAPL250221C00150000',  # OCC format            │
│     qty=9,                                                  │
│     side='buy',                                             │
│     type='limit',                                           │
│     limit_price=5.55,  # Slightly above ask                │
│     time_in_force='day',                                    │
│     order_class='bracket',  # Include stop-loss & target   │
│     stop_loss={'stop_price': 2.75},                        │
│     take_profit={'limit_price': 8.25}                      │
│ )                                                           │
│                                                             │
│ Order ID: abc-123-xyz ✅                                    │
│ Status: submitted                                           │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: WAIT FOR FILL (Alpaca processes order)             │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ Order submitted to market...                                │
│   ↓                                                         │
│ Market maker matches order...                               │
│   ↓                                                         │
│ Order filled! ✅                                            │
│                                                             │
│ Fill details:                                               │
│   - Filled qty: 9 contracts                                 │
│   - Fill price: $5.52 (slightly better than limit!)        │
│   - Fill time: 2025-01-15 10:32:15                         │
│   - Commission: $6.30 ($0.70 per contract)                 │
│   - Total cost: $4,974.30                                   │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: CREATE POSITION IN DATABASE                         │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ INSERT INTO positions (                                     │
│   signal_id, symbol, type, strike, expiration,             │
│   quantity, entry_price, entry_time,                        │
│   stop_loss, profit_target,                                 │
│   current_price, current_value, pnl, pnl_pct,              │
│   delta, gamma, theta, vega, iv,                           │
│   status, alpaca_order_id                                   │
│ ) VALUES (                                                  │
│   12345, 'AAPL', 'call', 150, '2025-02-21',                │
│   9, 5.52, '2025-01-15 10:32:15',                          │
│   2.75, 8.25,                                               │
│   5.52, 4968.00, 0, 0,                                     │
│   0.55, 0.03, -0.08, 0.15, 0.28,                           │
│   'open', 'abc-123-xyz'                                     │
│ )                                                           │
│                                                             │
│ Position ID: 67890 ✅                                       │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: UPDATE SIGNAL STATUS                                │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ UPDATE signals                                              │
│ SET status = 'executed',                                    │
│     executed_at = NOW(),                                    │
│     position_id = 67890                                     │
│ WHERE id = 12345                                            │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: NOTIFY USERS                                        │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ A. Publish to Redis:                                        │
│    PUBLISH position:opened {position_data}                  │
│                                                             │
│ B. Send to API Gateway:                                     │
│    → WebSocket broadcast to web clients                     │
│    → Dashboard updates in real-time                         │
│                                                             │
│ C. Send to Discord Bot:                                     │
│    → Post to TRADES channel:                                │
│      "✅ Trade Executed: AAPL 150 Call                      │
│       📈 Filled @ $5.52                                     │
│       📊 Quantity: 9 contracts                              │
│       💵 Total: $4,974.30"                                  │
│                                                             │
│ D. Optional: OpenAI generates insight:                      │
│    → "Great entry! Filled slightly below your limit         │
│       price. Position is now active and being monitored."   │
└─────────────────────────────────────────────────────────────┘
     ↓
Position Active! Now monitoring...
```

---

## 4. Position Management

### Continuous Monitoring (Every 3 Seconds)

```
┌─────────────────────────────────────────────────────────────┐
│           POSITION MONITORING LOOP                          │
│              (Runs every 3 seconds)                         │
└─────────────────────────────────────────────────────────────┘

TIMER TRIGGERS
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: FETCH ALL OPEN POSITIONS                            │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ SELECT * FROM positions                                     │
│ WHERE status = 'open'                                       │
│                                                             │
│ Result: [Position 67890: AAPL 150 Call, ...]               │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: GET CURRENT MARKET DATA                             │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ For each position, fetch from Polygon:                      │
│   - Current bid/ask                                         │
│   - Last trade price                                        │
│   - Volume                                                  │
│   - Updated Greeks                                          │
│   - Implied volatility                                      │
│                                                             │
│ AAPL 150 Call current data:                                 │
│   Bid: $7.20                                                │
│   Ask: $7.30                                                │
│   Last: $7.25                                               │
│   Delta: 0.68 (increased!)                                  │
│   Theta: -0.09                                              │
│   IV: 26% (decreased)                                       │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: CALCULATE P&L                                       │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ Entry price: $5.52 per contract                             │
│ Current price: $7.25 per contract                           │
│ Quantity: 9 contracts                                       │
│                                                             │
│ Entry value: 9 × $5.52 × 100 = $4,968                      │
│ Current value: 9 × $7.25 × 100 = $6,525                    │
│                                                             │
│ P&L: $6,525 - $4,968 = $1,557                              │
│ P&L %: ($1,557 / $4,968) × 100 = +31.3%                    │
│                                                             │
│ Status: 🟢 Winning position!                                │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: CHECK EXIT CONDITIONS                               │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ A. Profit Target Check:                                     │
│    Target: $8.25                                            │
│    Current: $7.25                                           │
│    Distance: 13.8% away                                     │
│    → Not reached yet                                        │
│                                                             │
│ B. Stop-Loss Check:                                         │
│    Stop: $2.75                                              │
│    Current: $7.25                                           │
│    Buffer: 163% above stop                                  │
│    → Safe                                                   │
│                                                             │
│ C. Time Decay Check:                                        │
│    Days to expiration: 37                                   │
│    Theta: -0.09 (losing $9/day)                            │
│    → Acceptable                                             │
│                                                             │
│ D. Delta Check:                                             │
│    Delta: 0.68 (good leverage)                              │
│    → Healthy                                                │
│                                                             │
│ Decision: HOLD ✅                                           │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: UPDATE DATABASE                                     │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ UPDATE positions                                            │
│ SET current_price = 7.25,                                   │
│     current_value = 6525.00,                                │
│     pnl = 1557.00,                                          │
│     pnl_pct = 31.3,                                         │
│     delta = 0.68,                                           │
│     theta = -0.09,                                          │
│     iv = 0.26,                                              │
│     last_updated = NOW()                                    │
│ WHERE id = 67890                                            │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: BROADCAST UPDATES                                   │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ If significant change (>5% P&L change):                     │
│                                                             │
│ A. Publish to Redis:                                        │
│    PUBLISH position:updated {position_data}                 │
│                                                             │
│ B. Send to API Gateway:                                     │
│    → WebSocket updates dashboard in real-time               │
│    → P&L chart updates                                      │
│                                                             │
│ C. Optional: Send to Discord (major milestones):            │
│    → "📊 AAPL 150 Call: +31.3% (+$1,557)"                  │
│                                                             │
│ D. Optional: OpenAI generates insight:                      │
│    → "Position performing well! Up 31% and approaching      │
│       profit target. Consider partial profit taking."       │
└─────────────────────────────────────────────────────────────┘
     ↓
Continue monitoring... (repeat every 3 seconds)
```

---

## 5. Risk Management

### Portfolio-Level Checks (Every 30 Seconds)

```
┌─────────────────────────────────────────────────────────────┐
│              RISK MANAGEMENT SYSTEM                         │
│             (Runs every 30 seconds)                         │
└─────────────────────────────────────────────────────────────┘

TIMER TRIGGERS
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: CALCULATE PORTFOLIO GREEKS                          │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ Sum all position Greeks:                                    │
│                                                             │
│ Position 1: AAPL 150 Call                                   │
│   Delta: 0.68 × 9 contracts = 6.12                         │
│   Gamma: 0.03 × 9 = 0.27                                    │
│   Vega: 0.15 × 9 = 1.35                                     │
│                                                             │
│ Position 2: TSLA 200 Put                                    │
│   Delta: -0.45 × 5 contracts = -2.25                       │
│   Gamma: 0.02 × 5 = 0.10                                    │
│   Vega: 0.12 × 5 = 0.60                                     │
│                                                             │
│ Position 3: MSFT 380 Call                                   │
│   Delta: 0.52 × 7 contracts = 3.64                         │
│   Gamma: 0.02 × 7 = 0.14                                    │
│   Vega: 0.10 × 7 = 0.70                                     │
│                                                             │
│ PORTFOLIO TOTALS:                                           │
│   Total Delta: 6.12 - 2.25 + 3.64 = 7.51                   │
│   Total Gamma: 0.27 + 0.10 + 0.14 = 0.51                   │
│   Total Vega: 1.35 + 0.60 + 0.70 = 2.65                    │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: CHECK RISK LIMITS                                   │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ ✅ Portfolio Delta: 7.51 (Limit: 100)                      │
│    Status: Safe - well below limit                          │
│                                                             │
│ ✅ Portfolio Gamma: 0.51 (Limit: 50)                       │
│    Status: Safe - minimal gamma risk                        │
│                                                             │
│ ✅ Portfolio Vega: 2.65 (Limit: 500)                       │
│    Status: Safe - low volatility exposure                   │
│                                                             │
│ ✅ Concentration Check:                                     │
│    Tech sector: 65% (Limit: 75%)                           │
│    AAPL: 28% (Limit: 25% - ⚠️ Warning!)                    │
│    Status: Approaching limit on AAPL                        │
│                                                             │
│ ✅ Daily Trades: 3 (Limit: 20)                             │
│    Status: Safe                                             │
│                                                             │
│ ✅ Buying Power: $25,000 available                         │
│    Status: Sufficient                                       │
│                                                             │
│ Overall Risk Level: LOW ✅                                  │
│ Warning: AAPL concentration approaching limit               │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: TAKE ACTION IF NEEDED                               │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ IF any limit exceeded:                                      │
│   → Block new signals for that symbol/sector                │
│   → Send alert to Discord ALERTS channel                    │
│   → Notify via web dashboard                                │
│   → Log to database                                         │
│                                                             │
│ IF critical risk (>90% of limit):                           │
│   → Suggest position reduction                              │
│   → Highlight in dashboard                                  │
│   → Generate OpenAI risk assessment                         │
│                                                             │
│ Current action:                                             │
│   → Send warning about AAPL concentration                   │
│   → Suggest diversification                                 │
└─────────────────────────────────────────────────────────────┘
     ↓
Continue monitoring... (repeat every 30 seconds)
```

---

## 6. Discord Integration

### Complete Discord Flow

```
┌─────────────────────────────────────────────────────────────┐
│              DISCORD INTEGRATION FLOW                       │
└─────────────────────────────────────────────────────────────┘

SIGNAL GENERATED in Trading Engine
     ↓
Trading Engine publishes event
     ↓
┌─────────────────────────────────────────────────────────────┐
│ DISCORD BOT RECEIVES EVENT                                  │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ Event: signal:new                                           │
│ Data: {                                                     │
│   id: 12345,                                                │
│   symbol: 'AAPL 150 Call',                                 │
│   confidence: 0.87,                                         │
│   entry: 5.50,                                              │
│   target: 8.25,                                             │
│   stop: 2.75,                                               │
│   explanation: '[OpenAI text]'                              │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ FORMAT MESSAGE                                              │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ If OpenAI enabled:                                          │
│   Use NLP service to generate friendly message             │
│                                                             │
│ Else:                                                       │
│   Use standard template                                     │
│                                                             │
│ Result:                                                     │
│ ┌───────────────────────────────────────────────────────┐ │
│ │ 🎯 New Signal: AAPL 150 Call                          │ │
│ │                                                       │ │
│ │ 📊 Confidence: 87% (High)                            │ │
│ │ 💰 Entry: $5.50                                      │ │
│ │ 🎯 Target: $8.25 (+50%)                              │ │
│ │ 🛑 Stop: $2.75 (-50%)                                │ │
│ │                                                       │ │
│ │ 💡 Why this trade looks good:                        │ │
│ │ • Technical breakout confirmed                       │ │
│ │ • Earnings beat drove momentum                       │ │
│ │ • News sentiment overwhelmingly bullish              │ │
│ │ • Excellent liquidity                                │ │
│ │                                                       │ │
│ │ React with ✅ to approve or ❌ to reject             │ │
│ └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ POST TO DISCORD CHANNEL                                     │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ 1. Get SIGNALS channel ID from config                       │
│ 2. Send message to channel                                  │
│ 3. Add reaction buttons: ✅ ❌                              │
│ 4. Store message ID for tracking                            │
│                                                             │
│ Message posted! ✅                                          │
└─────────────────────────────────────────────────────────────┘
     ↓
USER REACTS WITH ✅
     ↓
┌─────────────────────────────────────────────────────────────┐
│ DISCORD BOT CAPTURES REACTION                               │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ 1. Verify user is authorized (admin/owner)                  │
│ 2. Verify reaction is on a signal message                   │
│ 3. Extract signal ID from message                           │
│ 4. Determine action (✅ = approve, ❌ = reject)             │
│ 5. Send command to Trading Engine                           │
│                                                             │
│ Command sent: APPROVE signal 12345 ✅                       │
└─────────────────────────────────────────────────────────────┘
     ↓
Trading Engine executes trade (see Section 3)
     ↓
┌─────────────────────────────────────────────────────────────┐
│ DISCORD BOT RECEIVES EXECUTION EVENT                        │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ Event: position:opened                                      │
│ Data: {                                                     │
│   signal_id: 12345,                                         │
│   symbol: 'AAPL 150 Call',                                 │
│   quantity: 9,                                              │
│   fill_price: 5.52,                                         │
│   total_cost: 4974.30                                       │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ POST CONFIRMATION TO TRADES CHANNEL                         │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ ┌───────────────────────────────────────────────────────┐ │
│ │ ✅ Trade Executed: AAPL 150 Call                      │ │
│ │                                                       │ │
│ │ 📈 Filled @ $5.52                                    │ │
│ │ 📊 Quantity: 9 contracts                             │ │
│ │ 💵 Total: $4,974.30                                  │ │
│ │                                                       │ │
│ │ 🎯 Profit Target: $8.25                              │ │
│ │ 🛑 Stop Loss: $2.75                                  │ │
│ │                                                       │ │
│ │ Position is now active and being monitored! 📊       │ │
│ └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
     ↓
Continue monitoring for updates...
```

---

## 7. Data Flow

### Complete System Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│              COMPLETE SYSTEM DATA FLOW                      │
└─────────────────────────────────────────────────────────────┘

                    EXTERNAL APIs
                         ↓
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
    Alpaca API      Polygon API      NewsAPI
    (Trading)       (Market Data)    (Sentiment)
        ↓                ↓                ↓
        └────────────────┼────────────────┘
                         ↓
        ┌────────────────────────────────┐
        │     TRADING ENGINE (Python)    │
        │  ─────────────────────────────│
        │  • Signal Generation           │
        │  • Position Monitoring         │
        │  • Risk Management             │
        │  • Trade Execution             │
        └────────────────────────────────┘
                    ↓        ↑
                    ↓        ↑
        ┌───────────┴────────┴───────────┐
        │      PostgreSQL Database       │
        │  ─────────────────────────────│
        │  • Signals                     │
        │  • Positions                   │
        │  • Users                       │
        │  • Analytics                   │
        └────────────────────────────────┘
                    ↓        ↑
                    ↓        ↑
        ┌───────────┴────────┴───────────┐
        │        Redis Cache             │
        │  ─────────────────────────────│
        │  • Real-time events            │
        │  • WebSocket messages          │
        │  • Session data                │
        └────────────────────────────────┘
                    ↓        ↑
        ┌───────────┴────────┴───────────┐
        │    API GATEWAY (Node.js)       │
        │  ─────────────────────────────│
        │  • REST API                    │
        │  • WebSocket Server            │
        │  • Authentication              │
        └────────────────────────────────┘
            ↓               ↓
            ↓               ↓
    ┌───────┴───────┐   ┌──┴──────────────┐
    │  DISCORD BOT  │   │    FRONTEND     │
    │   (Node.js)   │   │     (React)     │
    │ ─────────────│   │ ───────────────│
    │ • Notifications│   │ • Dashboard     │
    │ • Approvals   │   │ • Charts        │
    │ • NLP Updates │   │ • Controls      │
    └───────────────┘   └─────────────────┘
            ↓                   ↓
            ↓                   ↓
        ┌───┴───────────────────┴───┐
        │          USER             │
        │  ───────────────────────  │
        │  • Discord notifications  │
        │  • Web dashboard          │
        │  • Approve/reject signals │
        └───────────────────────────┘
```

---

## 🎯 Summary

### Complete Lifecycle

1. **Startup** → System initializes all services
2. **Signal Generation** → AI analyzes markets every 5 minutes
3. **User Notification** → Discord + Web dashboard
4. **User Approval** → React to Discord or click web
5. **Trade Execution** → Order placed with Alpaca
6. **Position Monitoring** → Real-time tracking every 3 seconds
7. **Risk Management** → Portfolio checks every 30 seconds
8. **Exit** → Stop-loss or profit target hit
9. **Reporting** → Analytics updated, Discord notified

### Key Points

- ✅ **Fully Automated** - Runs 24/7 once configured
- ✅ **Real-Time** - Updates every 3 seconds
- ✅ **Multi-Factor** - Technical + Sentiment + Risk
- ✅ **Safe** - Manual approval required
- ✅ **Transparent** - Complete audit trail
- ✅ **Intelligent** - Optional OpenAI insights

---

**This is exactly what happens in your backend! 🚀**
