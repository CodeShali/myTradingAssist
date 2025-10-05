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

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
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
    
    echo -e "${BLUE}$prompt_text${NC}"
    
    if [ -n "$default_value" ]; then
        echo -e "${YELLOW}Current value: $default_value${NC}"
    fi
    
    if [ "$is_secret" = "true" ]; then
        read -s -p "Enter value (hidden): " value
        echo
    else
        read -p "Enter value: " value
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

# Alpaca API
echo -e "${GREEN}1. Alpaca API (Trading & Execution)${NC}"
echo -e "   Sign up at: ${BLUE}https://alpaca.markets${NC}"
ALPACA_API_KEY=$(prompt_input "ALPACA_API_KEY" "Alpaca API Key:" "" "false")
ALPACA_SECRET_KEY=$(prompt_input "ALPACA_SECRET_KEY" "Alpaca Secret Key:" "" "true")

echo -e "\n${YELLOW}Trading Mode:${NC}"
echo "  1) paper  - Paper trading (recommended for testing)"
echo "  2) live   - Live trading (real money)"
read -p "Select mode (1 or 2): " mode_choice

if [ "$mode_choice" = "2" ]; then
    TRADING_MODE="live"
    ALPACA_BASE_URL="https://api.alpaca.markets"
    echo -e "${RED}⚠️  WARNING: Live trading mode selected!${NC}"
else
    TRADING_MODE="paper"
    ALPACA_BASE_URL="https://paper-api.alpaca.markets"
    echo -e "${GREEN}✓ Paper trading mode selected${NC}"
fi

# Polygon API
echo -e "\n${GREEN}2. Polygon.io API (Market Data)${NC}"
echo -e "   Sign up at: ${BLUE}https://polygon.io${NC}"
POLYGON_API_KEY=$(prompt_input "POLYGON_API_KEY" "Polygon API Key:" "" "false")

# NewsAPI
echo -e "\n${GREEN}3. NewsAPI (News Sentiment)${NC}"
echo -e "   Sign up at: ${BLUE}https://newsapi.org${NC}"
NEWS_API_KEY=$(prompt_input "NEWS_API_KEY" "NewsAPI Key:" "" "false")

# Discord Bot
echo -e "\n${GREEN}4. Discord Bot${NC}"
echo -e "   Create bot at: ${BLUE}https://discord.com/developers/applications${NC}"
DISCORD_BOT_TOKEN=$(prompt_input "DISCORD_BOT_TOKEN" "Discord Bot Token:" "" "true")
DISCORD_GUILD_ID=$(prompt_input "DISCORD_GUILD_ID" "Discord Server ID:" "" "false")

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

# Discord Bot
DISCORD_BOT_TOKEN=$DISCORD_BOT_TOKEN
DISCORD_GUILD_ID=$DISCORD_GUILD_ID
DISCORD_ADMIN_USER_ID=

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
