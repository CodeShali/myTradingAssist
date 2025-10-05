# AI-Assisted Options Trading Platform

A comprehensive AI-powered options trading platform with multi-channel confirmation (Discord + Web UI), real-time position management, and automated exit strategies.

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway    │    │   External      │
│   Dashboard     │◄──►│   & Services     │◄──►│   APIs          │
│   (React)       │    │   (Node.js)      │    │   (Alpaca/etc)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Discord       │    │   Trading        │    │   PostgreSQL    │
│   Bot           │◄──►│   Engine         │◄──►│   Database      │
│   (Node.js)     │    │   (Python)       │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Redis         │    │   Analytics      │    │   Configuration │
│   Cache/Queue   │    │   Engine         │    │   Service       │
│                 │    │   (Python)       │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Features

### Core Trading Features
- **AI-Powered Signal Generation**: Automated analysis of options chains, market data, and news sentiment
- **Multi-Channel Confirmation**: Approve trades via Discord or Web Dashboard
- **Intelligent Order Execution**: Smart order routing with fallback strike management
- **Real-Time Position Tracking**: Live P&L, Greeks, and risk metrics
- **Automated Exit Management**: Profit targets and stop-loss automation
- **Comprehensive Analytics**: Performance tracking, strategy analysis, and reporting

### Risk Management
- Portfolio-level Greeks monitoring
- Concentration and correlation analysis
- Pattern day trading compliance
- Configurable position limits
- Real-time margin monitoring

### User Experience
- Paper trading mode for strategy testing
- Mobile-responsive web dashboard
- Discord bot for on-the-go management
- Real-time notifications across all channels
- Detailed trade journal and audit trail

## 📁 Project Structure

```
myTradingAssist/
├── backend/
│   ├── trading_engine/          # Python trading engine
│   │   ├── core/                # Core trading logic
│   │   ├── strategies/          # Trading strategies
│   │   ├── data/                # Market data providers
│   │   ├── execution/           # Order execution
│   │   ├── risk/                # Risk management
│   │   └── analytics/           # Analytics engine
│   ├── api_gateway/             # Node.js API server
│   │   ├── routes/              # API routes
│   │   ├── middleware/          # Auth, validation
│   │   └── websocket/           # Real-time updates
│   └── discord_bot/             # Discord integration
│       ├── commands/            # Bot commands
│       └── handlers/            # Event handlers
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── hooks/               # Custom hooks
│   │   ├── services/            # API services
│   │   └── utils/               # Utilities
│   └── public/                  # Static assets
├── database/
│   ├── migrations/              # Database migrations
│   └── seeds/                   # Seed data
├── config/
│   ├── development.json         # Dev configuration
│   ├── production.json          # Prod configuration
│   └── strategies.json          # Strategy definitions
├── tests/
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── e2e/                     # End-to-end tests
└── docs/
    ├── api/                     # API documentation
    ├── architecture/            # Architecture docs
    └── deployment/              # Deployment guides
```

## 🛠️ Technology Stack

### Backend
- **Python 3.11+**: Trading engine, analytics, AI models
- **Node.js 18+**: API gateway, Discord bot
- **PostgreSQL 15+**: Primary database
- **Redis 7+**: Caching and message queue
- **FastAPI**: Python REST API framework
- **Express.js**: Node.js web framework

### Frontend
- **React 18+**: UI framework
- **TypeScript**: Type safety
- **TailwindCSS**: Styling
- **shadcn/ui**: Component library
- **Recharts**: Data visualization
- **Socket.io**: Real-time updates

### External APIs
- **Alpaca**: Brokerage and market data
- **Polygon.io**: Options chain data
- **NewsAPI**: News sentiment
- **Discord API**: Bot integration

### AI/ML
- **FinBERT**: Sentiment analysis
- **scikit-learn**: Strategy optimization
- **pandas/numpy**: Data processing

## 📋 Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- PostgreSQL 15 or higher
- Redis 7 or higher
- Docker (optional, for containerized deployment)

## 🔧 Installation

### 1. Clone and Setup

```bash
cd myTradingAssist
```

### 2. Backend Setup (Python)

```bash
cd backend/trading_engine
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. API Gateway Setup (Node.js)

```bash
cd backend/api_gateway
npm install
```

### 4. Discord Bot Setup (Node.js)

```bash
cd backend/discord_bot
npm install
```

### 5. Frontend Setup (React)

```bash
cd frontend
npm install
```

### 6. Database Setup

```bash
# Create PostgreSQL database
createdb trading_platform

# Run migrations
cd database
psql trading_platform < migrations/001_initial_schema.sql
```

### 7. Configuration

Create `.env` files in each component directory:

**backend/trading_engine/.env**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/trading_platform
REDIS_URL=redis://localhost:6379
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret
POLYGON_API_KEY=your_polygon_key
NEWS_API_KEY=your_news_api_key
TRADING_MODE=paper  # or 'live'
```

**backend/api_gateway/.env**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/trading_platform
REDIS_URL=redis://localhost:6379
JWT_SECRET=your_jwt_secret
PORT=3000
```

**backend/discord_bot/.env**
```env
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_GUILD_ID=your_guild_id
API_GATEWAY_URL=http://localhost:3000
```

**frontend/.env**
```env
REACT_APP_API_URL=http://localhost:3000
REACT_APP_WS_URL=ws://localhost:3000
```

## 🚀 Running the Platform

### Development Mode

Start each component in separate terminals:

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Trading Engine
cd backend/trading_engine
source venv/bin/activate
python main.py

# Terminal 3: API Gateway
cd backend/api_gateway
npm run dev

# Terminal 4: Discord Bot
cd backend/discord_bot
npm run dev

# Terminal 5: Frontend
cd frontend
npm start
```

### Production Mode

```bash
# Use Docker Compose
docker-compose up -d
```

## 📊 Usage

### Initial Setup

1. **Access Web Dashboard**: Navigate to `http://localhost:3000`
2. **Configure Trading Parameters**:
   - Set position size limits
   - Define profit targets and stop-losses
   - Configure strategy preferences
   - Set liquidity requirements

3. **Connect Discord Bot**:
   - Invite bot to your Discord server
   - Use `/setup` command to link account
   - Configure notification preferences

### Trading Workflow

1. **Signal Generation**: AI analyzes market data and generates trade signals
2. **Confirmation**: Receive signals via Discord and/or Web Dashboard
3. **Execution**: Confirm trades within 5-minute window
4. **Monitoring**: Track positions in real-time across all channels
5. **Auto-Exit**: System automatically closes positions at targets/stops
6. **Analysis**: Review performance and optimize strategies

### Discord Commands

- `/signals` - View pending trade signals
- `/positions` - Show open positions
- `/pnl` - Display current P&L
- `/config` - Update trading configuration
- `/pause` - Pause signal generation
- `/resume` - Resume signal generation
- `/close <symbol>` - Manually close position

## 🧪 Testing

```bash
- **Prometheus Metrics**: `http://localhost:9090`
- **Application Logs**: `logs/` directory

## 🔒 Security
- JWT authentication for API access
- Encrypted database connections
- Rate limiting on all endpoints
- Audit logging for all trading actions
- Multi-factor authentication for live trading

## 🐛 Troubleshooting

### Common Issues

**Database Connection Errors**
```bash
# Check PostgreSQL is running
pg_isready

# Verify connection string
psql $DATABASE_URL
```

**Redis Connection Errors**
```bash
# Check Redis is running
redis-cli ping
```

**API Rate Limiting**
- Monitor API usage in dashboard
- Upgrade API plans if needed
- Implement request caching

## 📚 Documentation

- [API Documentation](docs/api/README.md)
- [Architecture Guide](docs/architecture/README.md)
- [Deployment Guide](docs/deployment/README.md)
- [Strategy Development](docs/strategies/README.md)

## 🤝 Contributing

This is a personal trading platform. For questions or issues, please create an issue in the repository.

## ⚠️ Disclaimer

This software is for educational and personal use only. Options trading involves substantial risk of loss. Past performance does not guarantee future results. Always understand the risks before trading with real capital.

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Alpaca for brokerage API
- Polygon.io for market data
- Discord for bot platform
- Open source community for amazing tools

---

**Built with ❤️ for systematic options trading**
