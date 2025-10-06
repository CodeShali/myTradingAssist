# System Architecture

## Overview

The AI-Assisted Options Trading Platform is a distributed system designed for real-time options trading with AI-powered signal generation, multi-channel confirmation, and automated position management.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interfaces                          │
├─────────────────────┬───────────────────────┬───────────────────┤
│   React Dashboard   │    Discord Bot        │   Mobile (Future) │
│   (Port 3001)       │    (Discord API)      │                   │
└──────────┬──────────┴───────────┬───────────┴───────────────────┘
           │                      │
           │ HTTP/WebSocket       │ Discord API
           │                      │
┌──────────▼──────────────────────▼───────────────────────────────┐
│                      API Gateway (Node.js)                       │
│                         Port 3000                                │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                │
│  │   Auth     │  │  Signals   │  │ Positions  │                │
│  │  Routes    │  │   Routes   │  │   Routes   │                │
│  └────────────┘  └────────────┘  └────────────┘                │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                │
│  │ Analytics  │  │   Users    │  │  Trading   │                │
│  │  Routes    │  │   Routes   │  │   Routes   │                │
│  └────────────┘  └────────────┘  └────────────┘                │
└──────────┬──────────────────────────────────────────────────────┘
           │
           │ PostgreSQL / Redis
           │
┌──────────▼──────────────────────────────────────────────────────┐
│                   Data Layer                                     │
├──────────────────────┬───────────────────────────────────────────┤
│   PostgreSQL DB      │         Redis Cache                       │
│   - Users            │         - Market Data Cache               │
│   - Signals          │         - Session Store                   │
│   - Positions        │         - Pub/Sub Channels                │
│   - Analytics        │         - Rate Limiting                   │
└──────────────────────┴───────────────────────────────────────────┘
           │
           │ Database Queries
           │
┌──────────▼──────────────────────────────────────────────────────┐
│              Trading Engine (Python)                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Signal Generator                               │ │
│  │  - Market Data Analysis                                     │ │
│  │  - News Sentiment Analysis                                  │ │
│  │  - Strategy Selection                                       │ │
│  │  - AI Decision Making                                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │            Position Manager                                 │ │
│  │  - Real-time Position Monitoring                            │ │
│  │  - P&L Calculation                                          │ │
│  │  - Auto-Exit Logic                                          │ │
│  │  - Greeks Calculation                                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │           Execution Service                                 │ │
│  │  - Order Placement                                          │ │
│  │  - Fill Monitoring                                          │ │
│  │  - Fallback Strike Management                               │ │
│  │  - Execution Quality Tracking                               │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────┬──────────────────────────────────────────────────────┘
           │
           │ API Calls
           │
┌──────────▼──────────────────────────────────────────────────────┐
│                   External Services                              │
├──────────────────┬──────────────────┬──────────────────────────┤
│   Alpaca API     │   Polygon API    │      NewsAPI             │
│   - Trading      │   - Options Data │      - News Feed         │
│   - Execution    │   - Market Data  │      - Headlines         │
└──────────────────┴──────────────────┴──────────────────────────┘
```

## Component Details

### 1. Frontend Layer

#### React Dashboard
- **Technology**: React 18, Vite, TailwindCSS
- **Features**:
  - Real-time position monitoring
  - Signal confirmation interface
  - Analytics and reporting
  - Configuration management
- **Communication**: REST API + WebSocket for real-time updates

#### Discord Bot
- **Technology**: Discord.js
- **Features**:
  - Trade signal notifications
  - Quick confirmation via reactions/buttons
  - Position updates
  - Command interface (!signals, !positions, !pnl)
- **Communication**: Discord API + Internal REST API

### 2. API Gateway Layer

#### Node.js Express Server
- **Port**: 3000
- **Responsibilities**:
  - Authentication & Authorization (JWT)
  - Request routing
  - Rate limiting
  - WebSocket management
  - Session management

#### Key Routes:
- `/api/auth` - Authentication
- `/api/signals` - Trade signals
- `/api/positions` - Position management
- `/api/analytics` - Performance metrics
- `/api/users` - User management
- `/api/trading` - Trading controls

### 3. Data Layer

#### PostgreSQL Database
- **Version**: 15+
- **Tables**:
  - `users` - User accounts
  - `user_configs` - Trading configurations
  - `trade_signals` - AI-generated signals
  - `executions` - Order executions
  - `positions` - Open/closed positions
  - `position_history` - Position snapshots
  - `market_data_cache` - Cached market data
  - `news_sentiment` - News analysis
  - `performance_metrics` - Analytics
  - `audit_log` - Audit trail

#### Redis Cache
- **Version**: 7+
- **Usage**:
  - Market data caching (5-second TTL)
  - Options chain caching (5-minute TTL)
  - Session storage
  - Pub/Sub for real-time events
  - Rate limiting counters

### 4. Trading Engine Layer

#### Signal Generator
- **Language**: Python 3.11+
- **Frequency**: Every 5 minutes
- **Process**:
  1. Fetch market data for watchlist symbols
  2. Analyze options chains for liquidity
  3. Fetch and analyze news sentiment
  4. Run AI strategy selection
  5. Generate trade signals
  6. Publish to Redis for notifications

#### Position Manager
- **Frequency**: Every 3 seconds
- **Process**:
  1. Fetch current prices for open positions
  2. Calculate unrealized P&L
  3. Update Greeks (delta, gamma, theta, vega)
  4. Check profit target conditions
  5. Check stop-loss conditions
  6. Execute auto-exits if triggered
  7. Record position history snapshots

#### Execution Service
- **Responsibilities**:
  - Pre-execution validation
  - Order placement via Alpaca API
  - Fill monitoring with timeout
  - Fallback strike handling
  - Execution quality tracking
  - Position creation

#### Market Data Service
- **Data Sources**:
  - Alpaca: Stock prices, historical data
  - Polygon: Options chains, option quotes
- **Caching Strategy**:
  - Stock prices: 5 seconds
  - Options chains: 5 minutes
  - Historical volatility: 1 hour
- **Rate Limiting**:
  - Alpaca: 200 req/min
  - Polygon: 5 req/min (free tier)

#### News Sentiment Service
- **Model**: FinBERT (Financial Sentiment Analysis)
- **Process**:
  1. Fetch news from NewsAPI
  2. Analyze sentiment (-1 to +1 scale)
  3. Categorize news (earnings, FDA, analyst, etc.)
  4. Determine impact level (low, medium, high)
  5. Apply veto rules for high-risk news

### 5. External Services

#### Alpaca Markets
- **Purpose**: Brokerage and execution
- **Features**:
  - Paper trading (free)
  - Live trading
  - Real-time market data
  - Order execution
- **Rate Limit**: 200 requests/minute

#### Polygon.io
- **Purpose**: Options data
- **Features**:
  - Options chains
  - Real-time quotes
  - Historical data
- **Rate Limit**: 5 requests/minute (free tier)

#### NewsAPI
- **Purpose**: News aggregation
- **Features**:
  - Multi-source news
  - Historical articles
  - Search and filtering
- **Rate Limit**: 1000 requests/day (free tier)

## Data Flow

### Signal Generation Flow

```
1. Timer triggers (every 5 min)
2. For each user:
   a. Get user config and watchlist
   b. For each symbol:
      - Fetch stock price
      - Fetch options chain
      - Fetch news sentiment
      - Check news veto conditions
      - Run strategy selector
      - Validate liquidity
      - Generate signal
   c. Store signal in database
   d. Publish to Redis
3. Discord bot receives signal
4. Web dashboard receives signal
5. User confirms via Discord or Web
6. API updates signal status
7. Trading engine executes order
8. Position created and monitored
```

### Position Monitoring Flow

```
1. Timer triggers (every 3 sec)
2. Get all open positions
3. For each position:
   a. Fetch current option price
   b. Calculate P&L
   c. Update Greeks
   d. Check profit target
   e. Check stop loss
   f. If exit condition met:
      - Execute closing order
      - Update position status
      - Publish notification
   g. Record history snapshot
4. Publish updates to WebSocket
```

## Scalability Considerations

### Horizontal Scaling
- **API Gateway**: Stateless, can run multiple instances behind load balancer
- **Trading Engine**: Single instance per user (to avoid duplicate signals)
- **Database**: Read replicas for analytics queries
- **Redis**: Redis Cluster for high availability

### Vertical Scaling
- **Database**: Increase connection pool size
- **Redis**: Increase memory allocation
- **Trading Engine**: Optimize signal generation algorithms

### Performance Optimizations
- Market data caching (reduce API calls)
- Database query optimization (indexes, materialized views)
- Async processing for non-critical operations
- WebSocket for real-time updates (vs polling)

## Security Architecture

### Authentication
- JWT tokens with 7-day expiration
- Bcrypt password hashing (10 rounds)
- Session management via Redis

### Authorization
- Role-based access control
- User-specific data isolation
- API key rotation for external services

### Data Protection
- HTTPS/TLS for all external communication
- Encrypted database connections
- Sensitive data encryption at rest
- API keys in environment variables (never in code)

### Audit Trail
- All trading actions logged
- User actions tracked
- System events recorded
- Compliance reporting

## Monitoring & Observability

### Logging
- Structured logging (JSON format)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Separate logs for:
  - Application logs
  - Trading activity
  - Error logs
  - Audit logs

### Metrics
- Prometheus for metrics collection
- Grafana for visualization
- Key metrics:
  - API response times
  - Database query performance
  - Signal generation latency
  - Order execution quality
  - System resource usage

### Health Checks
- API health endpoint: `/health`
- Database connection checks
- Redis connection checks
- External API connectivity checks
- Automated alerting on failures

## Disaster Recovery

### Backup Strategy
- Database: Daily automated backups
- Configuration: Version controlled
- Logs: Retained for 30 days
- Critical data: Real-time replication

### Recovery Procedures
- Database restore from backup
- Service restart procedures
- Failover to backup systems
- Data reconciliation processes

## Future Enhancements

1. **Machine Learning**:
   - Deep learning for signal generation
   - Reinforcement learning for strategy optimization
   - Predictive analytics for risk management

2. **Advanced Features**:
   - Multi-leg option strategies
   - Portfolio optimization
   - Backtesting framework
   - Paper trading simulator

3. **Scalability**:
   - Microservices architecture
   - Kubernetes deployment
   - Multi-region support
   - CDN for frontend assets

4. **Integrations**:
   - Additional brokers (TD Ameritrade, Interactive Brokers)
   - Alternative data sources
   - Tax reporting integration
   - Mobile app (iOS/Android)
