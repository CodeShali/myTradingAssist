#!/bin/bash

#############################################################################
# Environment Configuration Script
# Interactive setup for .env file
#############################################################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Get the actual project root (two levels up from this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"

clear
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   Environment Configuration Setup                            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF

echo -e "\n${CYAN}This wizard will help you configure your environment variables.${NC}\n"

# Function to prompt for input
prompt_input() {
    local var_name=$1
    local prompt_text=$2
    local default_value=$3
    local is_secret=$4
    
    if [ -n "$default_value" ]; then
        echo -e "${YELLOW}Current value: $default_value${NC}"
    fi
    
    if [ "$is_secret" = "true" ]; then
        read -s -p "${prompt_text} " value
        echo
    else
        read -p "${prompt_text} " value
    fi
    
    if [ -z "$value" ] && [ -n "$default_value" ]; then
        value="$default_value"
    fi
    
    echo "$value"
}

# Generate random secret
generate_secret() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-32
}

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}API Keys Configuration${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Trading Mode Selection (FIRST - determines which API keys to use)
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Trading Mode Selection${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${CYAN}Choose your trading mode:${NC}"
echo "  1) paper  - Paper trading (recommended for testing)"
echo "  2) live   - Live trading (real money)"
echo ""
read -p "Select mode (1 or 2): " mode_choice

if [ "$mode_choice" = "2" ]; then
    TRADING_MODE="live"
    ALPACA_BASE_URL="https://api.alpaca.markets"
    echo -e "\n${RED}⚠️  WARNING: Live trading mode selected!${NC}"
    echo -e "${RED}⚠️  You will need LIVE API keys from Alpaca${NC}\n"
else
    TRADING_MODE="paper"
    ALPACA_BASE_URL="https://paper-api.alpaca.markets"
    echo -e "\n${GREEN}✓ Paper trading mode selected${NC}"
    echo -e "${GREEN}✓ You will need PAPER API keys from Alpaca${NC}\n"
fi

# Alpaca API
echo -e "${GREEN}1. Alpaca API (Trading & Execution)${NC}"
echo -e "   Sign up at: ${BLUE}https://alpaca.markets${NC}"

if [ "$TRADING_MODE" = "paper" ]; then
    echo -e "${YELLOW}   ⚠️  IMPORTANT: Use PAPER TRADING API keys${NC}"
    echo -e "${YELLOW}   Go to: Paper Trading → Generate API Key${NC}"
else
    echo -e "${RED}   ⚠️  IMPORTANT: Use LIVE TRADING API keys${NC}"
    echo -e "${RED}   Go to: Live Trading → Generate API Key${NC}"
fi

echo ""
echo -e "${YELLOW}You'll need TWO values from Alpaca:${NC}"
echo "  1. API Key ID (starts with 'PK' for paper or 'AK' for live)"
echo "  2. Secret Key (long alphanumeric string)"
echo ""
ALPACA_API_KEY=$(prompt_input "ALPACA_API_KEY" "Alpaca API Key ID ($TRADING_MODE):" "" "false")
ALPACA_SECRET_KEY=$(prompt_input "ALPACA_SECRET_KEY" "Alpaca Secret Key ($TRADING_MODE):" "" "false")

# Polygon API
echo -e "\n${GREEN}2. Polygon.io API (Market Data)${NC}"
echo -e "   Sign up at: ${BLUE}https://polygon.io${NC}"
echo -e "   ${YELLOW}Used for: Options chains, stock quotes, historical data${NC}"
echo ""
POLYGON_API_KEY=$(prompt_input "POLYGON_API_KEY" "Polygon API Key:" "" "false")

# NewsAPI
echo -e "\n${GREEN}3. NewsAPI (News Sentiment)${NC}"
echo -e "   Sign up at: ${BLUE}https://newsapi.org${NC}"
echo -e "   ${YELLOW}Used for: News headlines and sentiment analysis${NC}"
echo ""
NEWS_API_KEY=$(prompt_input "NEWS_API_KEY" "NewsAPI Key:" "" "false")

# Discord Bot
echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}4. Discord Bot Configuration (Optional)${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}Discord Setup Steps:${NC}"
echo "1. Go to: https://discord.com/developers/applications"
echo "2. Click 'New Application' → Give it a name (e.g., 'OptionsAI Bot')"
echo "3. Go to 'Bot' section → Click 'Add Bot'"
echo "4. Copy the Bot Token"
echo "5. Go to 'OAuth2' → 'URL Generator'"
echo "   - Select scopes: bot"
echo "   - Select permissions: Send Messages, Read Messages, Add Reactions"
echo "   - Copy the generated URL and invite bot to your server"
echo ""
echo -e "${YELLOW}To get Channel IDs:${NC}"
echo "1. In Discord: Settings → Advanced → Enable 'Developer Mode'"
echo "2. Right-click any channel → 'Copy ID'"
echo ""

read -p "Do you want to configure Discord? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${CYAN}Step 1: Application & Bot Information${NC}"
    echo "─────────────────────────────────────────"
    echo ""
    echo -e "${YELLOW}What you need (from https://discord.com/developers/applications):${NC}"
    echo "  • Application ID - Numbers only (e.g., 1424594241362989086)"
    echo "  • Public Key - Long hex string (e.g., ca806fe10fe398...)"
    echo "  • Bot Token - From Bot page (e.g., MTIzNDU2Nzg5...)"
    echo ""
    echo -e "${RED}⚠️  DO NOT enter the OAuth2 URL!${NC}"
    echo ""
    
    DISCORD_APPLICATION_ID=$(prompt_input "DISCORD_APPLICATION_ID" "Application ID:" "" "false")
    DISCORD_PUBLIC_KEY=$(prompt_input "DISCORD_PUBLIC_KEY" "Public Key:" "" "false")
    DISCORD_BOT_TOKEN=$(prompt_input "DISCORD_BOT_TOKEN" "Bot Token:" "" "false")
    
    echo ""
    echo -e "${CYAN}Step 2: Server Information${NC}"
    echo "─────────────────────────────────────────"
    echo ""
    echo -e "${YELLOW}What you need:${NC}"
    echo "  • Server ID - Right-click your server name → Copy ID"
    echo "  • Example: 987654321098765432"
    echo ""
    
    DISCORD_GUILD_ID=$(prompt_input "DISCORD_GUILD_ID" "Server ID:" "" "false")
    
    echo ""
    echo -e "${CYAN}Step 3: Channel IDs (Optional - press Enter to skip any)${NC}"
    echo "─────────────────────────────────────────"
    echo ""
    echo -e "${YELLOW}How to get Channel IDs:${NC}"
    echo "  1. In Discord: Settings → Advanced → Enable 'Developer Mode'"
    echo "  2. Right-click any channel → 'Copy ID'"
    echo "  3. Each ID is a long number (e.g., 1315816955353239583)"
    echo ""
    echo -e "${YELLOW}Channel Types (what each is for):${NC}"
    echo "  • Main Channel     - General notifications"
    echo "  • Signals Channel  - AI signals (you approve with ✅ or ❌)"
    echo "  • Trades Channel   - Trade confirmations"
    echo "  • Alerts Channel   - Risk warnings"
    echo "  • Updates Channel  - Daily summaries"
    echo ""
    echo -e "${CYAN}💡 Tip: You can use the same channel ID for all, or create separate channels${NC}"
    echo ""
    
    DISCORD_CHANNEL_ID=$(prompt_input "DISCORD_CHANNEL_ID" "Main Channel ID:" "" "false")
    DISCORD_SIGNALS_CHANNEL_ID=$(prompt_input "DISCORD_SIGNALS_CHANNEL_ID" "Signals Channel ID (or press Enter to use Main):" "" "false")
    DISCORD_TRADES_CHANNEL_ID=$(prompt_input "DISCORD_TRADES_CHANNEL_ID" "Trades Channel ID (or press Enter to use Main):" "" "false")
    DISCORD_ALERTS_CHANNEL_ID=$(prompt_input "DISCORD_ALERTS_CHANNEL_ID" "Alerts Channel ID (or press Enter to use Main):" "" "false")
    DISCORD_UPDATES_CHANNEL_ID=$(prompt_input "DISCORD_UPDATES_CHANNEL_ID" "Updates Channel ID (or press Enter to use Main):" "" "false")
    
    # If no channels specified, use main channel for everything
    if [ -z "$DISCORD_SIGNALS_CHANNEL_ID" ]; then
        DISCORD_SIGNALS_CHANNEL_ID="$DISCORD_CHANNEL_ID"
    fi
    if [ -z "$DISCORD_TRADES_CHANNEL_ID" ]; then
        DISCORD_TRADES_CHANNEL_ID="$DISCORD_CHANNEL_ID"
    fi
    if [ -z "$DISCORD_ALERTS_CHANNEL_ID" ]; then
        DISCORD_ALERTS_CHANNEL_ID="$DISCORD_CHANNEL_ID"
    fi
    if [ -z "$DISCORD_UPDATES_CHANNEL_ID" ]; then
        DISCORD_UPDATES_CHANNEL_ID="$DISCORD_CHANNEL_ID"
    fi
    
    echo ""
    echo -e "${GREEN}✓ Discord configured!${NC}"
else
    DISCORD_APPLICATION_ID=""
    DISCORD_PUBLIC_KEY=""
    DISCORD_BOT_TOKEN=""
    DISCORD_GUILD_ID=""
    DISCORD_CHANNEL_ID=""
    DISCORD_SIGNALS_CHANNEL_ID=""
    DISCORD_TRADES_CHANNEL_ID=""
    DISCORD_ALERTS_CHANNEL_ID=""
    DISCORD_UPDATES_CHANNEL_ID=""
    echo -e "${YELLOW}Skipping Discord configuration${NC}"
fi

# OpenAI (Optional)
echo -e "\n${GREEN}5. OpenAI API (Optional - for enhanced NLP features)${NC}"
echo -e "   Sign up at: ${BLUE}https://platform.openai.com${NC}"
echo -e "   ${YELLOW}Note: Platform works great without OpenAI!${NC}"
OPENAI_API_KEY=$(prompt_input "OPENAI_API_KEY" "OpenAI API Key (or press Enter to skip):" "" "true")

if [ -n "$OPENAI_API_KEY" ]; then
    echo -e "   ${YELLOW}Choose model:${NC}"
    echo "   1) gpt-4 (best quality, higher cost)"
    echo "   2) gpt-3.5-turbo (good quality, lower cost)"
    read -p "   Select (1 or 2, default: 2): " model_choice
    
    if [ "$model_choice" = "1" ]; then
        OPENAI_MODEL="gpt-4"
    else
        OPENAI_MODEL="gpt-3.5-turbo"
    fi
else
    OPENAI_MODEL=""
fi

echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Database Configuration${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

POSTGRES_PASSWORD=$(prompt_input "POSTGRES_PASSWORD" "PostgreSQL Password:" "changeme" "true")
DATABASE_URL="postgresql://trading_user:${POSTGRES_PASSWORD}@localhost:5432/trading_platform"
REDIS_URL="redis://localhost:6379"

echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Security Configuration${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${YELLOW}Generating secure random keys...${NC}"
JWT_SECRET=$(generate_secret)
SESSION_SECRET=$(generate_secret)
echo -e "${GREEN}✓ Security keys generated${NC}"

echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Trading Parameters${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

MAX_POSITION_SIZE_PCT=$(prompt_input "MAX_POSITION_SIZE_PCT" "Max Position Size (% of portfolio):" "10" "false")
MAX_DAILY_TRADES=$(prompt_input "MAX_DAILY_TRADES" "Max Daily Trades:" "20" "false")
DEFAULT_PROFIT_TARGET_PCT=$(prompt_input "DEFAULT_PROFIT_TARGET_PCT" "Default Profit Target (%):" "50" "false")
DEFAULT_STOP_LOSS_PCT=$(prompt_input "DEFAULT_STOP_LOSS_PCT" "Default Stop Loss (%):" "50" "false")

# Write .env file
echo -e "\n${YELLOW}Writing configuration to .env file...${NC}"

cat > "$ENV_FILE" << EOF
# Database Configuration
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
DATABASE_URL=$DATABASE_URL

# Redis Configuration
REDIS_URL=$REDIS_URL

# API Keys - External Services
ALPACA_API_KEY=$ALPACA_API_KEY
ALPACA_SECRET_KEY=$ALPACA_SECRET_KEY
ALPACA_BASE_URL=$ALPACA_BASE_URL
POLYGON_API_KEY=$POLYGON_API_KEY
NEWS_API_KEY=$NEWS_API_KEY

# Trading Configuration
TRADING_MODE=$TRADING_MODE
MAX_POSITION_SIZE_PCT=$MAX_POSITION_SIZE_PCT
MAX_DAILY_TRADES=$MAX_DAILY_TRADES
DEFAULT_PROFIT_TARGET_PCT=$DEFAULT_PROFIT_TARGET_PCT
DEFAULT_STOP_LOSS_PCT=$DEFAULT_STOP_LOSS_PCT

# Security
JWT_SECRET=$JWT_SECRET
SESSION_SECRET=$SESSION_SECRET

# Discord Bot Configuration
DISCORD_APPLICATION_ID=$DISCORD_APPLICATION_ID
DISCORD_PUBLIC_KEY=$DISCORD_PUBLIC_KEY
DISCORD_BOT_TOKEN=$DISCORD_BOT_TOKEN
DISCORD_GUILD_ID=$DISCORD_GUILD_ID
DISCORD_ADMIN_USER_ID=
DISCORD_CHANNEL_ID=$DISCORD_CHANNEL_ID
DISCORD_SIGNALS_CHANNEL_ID=$DISCORD_SIGNALS_CHANNEL_ID
DISCORD_TRADES_CHANNEL_ID=$DISCORD_TRADES_CHANNEL_ID
DISCORD_ALERTS_CHANNEL_ID=$DISCORD_ALERTS_CHANNEL_ID
DISCORD_UPDATES_CHANNEL_ID=$DISCORD_UPDATES_CHANNEL_ID

# OpenAI Configuration (Optional)
OPENAI_API_KEY=$OPENAI_API_KEY
OPENAI_MODEL=$OPENAI_MODEL

# API Gateway
API_GATEWAY_PORT=3000
API_GATEWAY_URL=http://localhost:3000

# Frontend
REACT_APP_API_URL=http://localhost:3000
REACT_APP_WS_URL=ws://localhost:3000
VITE_API_URL=http://localhost:3000

# Monitoring
GRAFANA_PASSWORD=admin

# Logging
LOG_LEVEL=info
LOG_TO_FILE=true

# Feature Flags
ENABLE_AUTO_TRADING=true
ENABLE_NEWS_SENTIMENT=true
ENABLE_DISCORD_NOTIFICATIONS=true
ENABLE_WEB_NOTIFICATIONS=true

# Rate Limiting
ALPACA_RATE_LIMIT=200
POLYGON_RATE_LIMIT=5
NEWS_API_RATE_LIMIT=1000

# Risk Management
MAX_PORTFOLIO_DELTA=100
MAX_PORTFOLIO_GAMMA=50
MAX_PORTFOLIO_VEGA=500
MAX_CONCENTRATION_PCT=25

# Signal Generation
SIGNAL_GENERATION_INTERVAL=300
SIGNAL_EXPIRATION_TIME=300
MIN_LIQUIDITY_SCORE=0.6
MAX_BID_ASK_SPREAD_PCT=5

# Position Management
POSITION_UPDATE_INTERVAL=3
AUTO_SELL_ENABLED=true
TRAILING_STOP_ENABLED=false

# Analytics
ANALYTICS_UPDATE_INTERVAL=60
PERFORMANCE_LOOKBACK_DAYS=365
EOF

chmod 600 "$ENV_FILE"

echo -e "${GREEN}✓ Configuration saved to .env${NC}"

# Summary
echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Configuration Summary${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${GREEN}Trading Mode:${NC} $TRADING_MODE"
echo -e "${GREEN}Max Position Size:${NC} $MAX_POSITION_SIZE_PCT%"
echo -e "${GREEN}Max Daily Trades:${NC} $MAX_DAILY_TRADES"
echo -e "${GREEN}Profit Target:${NC} $DEFAULT_PROFIT_TARGET_PCT%"
echo -e "${GREEN}Stop Loss:${NC} $DEFAULT_STOP_LOSS_PCT%"

echo -e "\n${YELLOW}⚠️  Security Reminder:${NC}"
echo -e "  • Never commit .env to version control"
echo -e "  • Keep your API keys secure"
echo -e "  • Rotate keys regularly"

if [ "$TRADING_MODE" = "live" ]; then
    echo -e "\n${RED}⚠️  LIVE TRADING WARNING:${NC}"
    echo -e "  • You are using LIVE trading mode"
    echo -e "  • Real money will be at risk"
    echo -e "  • Test thoroughly in paper mode first"
fi

echo -e "\n${GREEN}✓ Environment configuration complete!${NC}"
echo -e "${BLUE}You can now run: ./start.sh${NC}\n"
