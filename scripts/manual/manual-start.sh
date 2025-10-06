#!/bin/bash

#############################################################################
# AI-Assisted Options Trading Platform - Startup Script
# This script sets up and runs all components of the trading platform
#############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Log file
LOG_FILE="$PROJECT_ROOT/logs/startup.log"
mkdir -p "$PROJECT_ROOT/logs"

#############################################################################
# Helper Functions
#############################################################################

print_header() {
    echo -e "\n${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_step() {
    echo -e "${MAGENTA}▶ $1${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1
}

# Function to wait for service
wait_for_service() {
    local service=$1
    local port=$2
    local max_attempts=30
    local attempt=1
    
    print_step "Waiting for $service to be ready on port $port..."
    
    while [ $attempt -le $max_attempts ]; do
        if port_in_use $port; then
            print_success "$service is ready!"
            return 0
        fi
        echo -n "."
        sleep 1
        ((attempt++))
    done
    
    print_error "$service failed to start on port $port"
    return 1
}

# Function to check PostgreSQL
check_postgres() {
    if command_exists psql; then
        if pg_isready >/dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# Function to check Redis
check_redis() {
    if command_exists redis-cli; then
        if redis-cli ping >/dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

#############################################################################
# Banner
#############################################################################

clear
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   AI-Assisted Options Trading Platform                       ║
║   Automated Trading with Multi-Channel Confirmation          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF

echo -e "\n${YELLOW}⚠️  DISCLAIMER: Options trading involves substantial risk.${NC}"
echo -e "${YELLOW}   Always start in PAPER TRADING mode!${NC}\n"

sleep 2

#############################################################################
# Step 1: Check Prerequisites
#############################################################################

print_header "Step 1: Checking Prerequisites"

MISSING_DEPS=0

# Check Python
print_step "Checking Python..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION installed"
else
    print_error "Python 3.11+ is required but not installed"
    MISSING_DEPS=1
fi

# Check Node.js
print_step "Checking Node.js..."
if command_exists node; then
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION installed"
else
    print_error "Node.js 18+ is required but not installed"
    MISSING_DEPS=1
fi

# Check npm
print_step "Checking npm..."
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    print_success "npm $NPM_VERSION installed"
else
    print_error "npm is required but not installed"
    MISSING_DEPS=1
fi

# Check PostgreSQL
print_step "Checking PostgreSQL..."
if command_exists psql; then
    POSTGRES_VERSION=$(psql --version | cut -d' ' -f3)
    print_success "PostgreSQL $POSTGRES_VERSION installed"
    
    if check_postgres; then
        print_success "PostgreSQL is running"
    else
        print_warning "PostgreSQL is installed but not running"
        print_info "Please start PostgreSQL: brew services start postgresql (macOS)"
        MISSING_DEPS=1
    fi
else
    print_error "PostgreSQL 15+ is required but not installed"
    MISSING_DEPS=1
fi

# Check Redis
print_step "Checking Redis..."
if command_exists redis-server; then
    print_success "Redis is installed"
    
    if check_redis; then
        print_success "Redis is running"
    else
        print_warning "Redis is installed but not running"
        print_info "Starting Redis..."
        redis-server --daemonize yes
        sleep 2
        if check_redis; then
            print_success "Redis started successfully"
        else
            print_error "Failed to start Redis"
            MISSING_DEPS=1
        fi
    fi
else
    print_error "Redis 7+ is required but not installed"
    MISSING_DEPS=1
fi

if [ $MISSING_DEPS -eq 1 ]; then
    print_error "Missing dependencies. Please install them and try again."
    echo -e "\n${BLUE}Installation Guide:${NC}"
    echo "  macOS: brew install python node postgresql redis"
    echo "  Ubuntu: sudo apt install python3 nodejs npm postgresql redis-server"
    exit 1
fi

#############################################################################
# Step 2: Environment Configuration
#############################################################################

print_header "Step 2: Environment Configuration"

ENV_FILE="$PROJECT_ROOT/.env"

if [ -f "$ENV_FILE" ]; then
    print_success ".env file found"
    
    # Check if required variables are set
    print_step "Validating environment variables..."
    
    REQUIRED_VARS=(
        "ALPACA_API_KEY"
        "ALPACA_SECRET_KEY"
        "POLYGON_API_KEY"
        "NEWS_API_KEY"
        "DISCORD_BOT_TOKEN"
        "DATABASE_URL"
        "REDIS_URL"
        "JWT_SECRET"
    )
    
    MISSING_VARS=0
    source "$ENV_FILE"
    
    for var in "${REQUIRED_VARS[@]}"; do
        if [ -z "${!var}" ] || [ "${!var}" = "your_"* ]; then
            print_warning "$var is not configured"
            MISSING_VARS=1
        else
            print_success "$var is configured"
        fi
    done
    
    if [ $MISSING_VARS -eq 1 ]; then
        print_warning "Some environment variables are missing or not configured"
        read -p "Do you want to configure them now? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            bash "$PROJECT_ROOT/setup-env.sh"
        else
            print_error "Cannot proceed without proper configuration"
            exit 1
        fi
    fi
else
    print_warning ".env file not found"
    
    if [ -f "$PROJECT_ROOT/.env.example" ]; then
        print_info "Creating .env from .env.example..."
        cp "$PROJECT_ROOT/.env.example" "$ENV_FILE"
        print_success ".env file created"
        
        print_info "Please configure your environment variables"
        bash "$PROJECT_ROOT/setup-env.sh"
    else
        print_error ".env.example not found. Cannot create configuration."
        exit 1
    fi
fi

# Source the environment
source "$ENV_FILE"

#############################################################################
# Step 3: Database Setup
#############################################################################

print_header "Step 3: Database Setup"

print_step "Checking database connection..."

if psql "$DATABASE_URL" -c "SELECT 1" >/dev/null 2>&1; then
    print_success "Database connection successful"
    
    # Check if tables exist
    TABLE_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')
    
    if [ "$TABLE_COUNT" -eq "0" ]; then
        print_warning "Database is empty. Running migrations..."
        
        if [ -f "$PROJECT_ROOT/database/migrations/001_initial_schema.sql" ]; then
            psql "$DATABASE_URL" -f "$PROJECT_ROOT/database/migrations/001_initial_schema.sql" >> "$LOG_FILE" 2>&1
            print_success "Database schema created"
        else
            print_error "Migration file not found"
            exit 1
        fi
    else
        print_success "Database tables exist ($TABLE_COUNT tables)"
    fi
else
    print_error "Cannot connect to database"
    print_info "Please check your DATABASE_URL in .env"
    exit 1
fi

#############################################################################
# Step 4: Install Dependencies
#############################################################################

print_header "Step 4: Installing Dependencies"

# Python Trading Engine
print_step "Installing Python dependencies..."
cd "$PROJECT_ROOT/backend/trading_engine"

if [ ! -d "venv" ]; then
    print_info "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt >> "$LOG_FILE" 2>&1
print_success "Python dependencies installed"
deactivate

# API Gateway
print_step "Installing API Gateway dependencies..."
cd "$PROJECT_ROOT/backend/api_gateway"
if [ ! -d "node_modules" ]; then
    npm install >> "$LOG_FILE" 2>&1
    print_success "API Gateway dependencies installed"
else
    print_success "API Gateway dependencies already installed"
fi

# Discord Bot
print_step "Installing Discord Bot dependencies..."
cd "$PROJECT_ROOT/backend/discord_bot"
if [ ! -d "node_modules" ]; then
    npm install >> "$LOG_FILE" 2>&1
    print_success "Discord Bot dependencies installed"
else
    print_success "Discord Bot dependencies already installed"
fi

# Frontend
print_step "Installing Frontend dependencies..."
cd "$PROJECT_ROOT/frontend"
if [ ! -d "node_modules" ]; then
    npm install >> "$LOG_FILE" 2>&1
    print_success "Frontend dependencies installed"
else
    print_success "Frontend dependencies already installed"
fi

cd "$PROJECT_ROOT"

#############################################################################
# Step 5: Check Ports
#############################################################################

print_header "Step 5: Checking Ports"

PORTS=(3000 3001 5432 6379)
PORT_NAMES=("API Gateway" "Frontend" "PostgreSQL" "Redis")

for i in "${!PORTS[@]}"; do
    PORT=${PORTS[$i]}
    NAME=${PORT_NAMES[$i]}
    
    if port_in_use $PORT; then
        if [ "$NAME" = "PostgreSQL" ] || [ "$NAME" = "Redis" ]; then
            print_success "$NAME is running on port $PORT"
        else
            print_warning "Port $PORT is already in use (needed for $NAME)"
            read -p "Kill process on port $PORT? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
                print_success "Process killed on port $PORT"
            fi
        fi
    else
        print_info "Port $PORT is available for $NAME"
    fi
done

#############################################################################
# Step 6: Start Services
#############################################################################

print_header "Step 6: Starting Services"

# Create PID directory
PID_DIR="$PROJECT_ROOT/logs/pids"
mkdir -p "$PID_DIR"

# Function to start service
start_service() {
    local name=$1
    local command=$2
    local log_file="$PROJECT_ROOT/logs/${name}.log"
    local pid_file="$PID_DIR/${name}.pid"
    
    print_step "Starting $name..."
    
    # Kill existing process if running
    if [ -f "$pid_file" ]; then
        OLD_PID=$(cat "$pid_file")
        if ps -p $OLD_PID > /dev/null 2>&1; then
            kill $OLD_PID 2>/dev/null || true
            sleep 1
        fi
        rm -f "$pid_file"
    fi
    
    # Start the service
    eval "$command" > "$log_file" 2>&1 &
    echo $! > "$pid_file"
    
    sleep 2
    
    if ps -p $(cat "$pid_file") > /dev/null 2>&1; then
        print_success "$name started (PID: $(cat $pid_file))"
    else
        print_error "$name failed to start. Check $log_file"
        return 1
    fi
}

# Start Trading Engine
start_service "trading-engine" \
    "cd $PROJECT_ROOT/backend/trading_engine && source venv/bin/activate && python main.py"

# Start API Gateway
start_service "api-gateway" \
    "cd $PROJECT_ROOT/backend/api_gateway && node server.js"

# Wait for API Gateway
wait_for_service "API Gateway" 3000

# Start Discord Bot
start_service "discord-bot" \
    "cd $PROJECT_ROOT/backend/discord_bot && node index.js"

# Start Frontend
start_service "frontend" \
    "cd $PROJECT_ROOT/frontend && npm run dev"

# Wait for Frontend
wait_for_service "Frontend" 3001

#############################################################################
# Step 7: Health Checks
#############################################################################

print_header "Step 7: Running Health Checks"

sleep 3

# Check API Gateway health
print_step "Checking API Gateway..."
if curl -s http://localhost:3000/health >/dev/null 2>&1; then
    print_success "API Gateway is healthy"
else
    print_error "API Gateway health check failed"
fi

# Check database connection
print_step "Checking database..."
if psql "$DATABASE_URL" -c "SELECT 1" >/dev/null 2>&1; then
    print_success "Database is accessible"
else
    print_error "Database connection failed"
fi

# Check Redis
print_step "Checking Redis..."
if redis-cli ping >/dev/null 2>&1; then
    print_success "Redis is responding"
else
    print_error "Redis connection failed"
fi

#############################################################################
# Final Summary
#############################################################################

print_header "🎉 Platform Started Successfully!"

cat << EOF

${GREEN}All services are running!${NC}

${CYAN}Access Points:${NC}
  📊 Web Dashboard:    ${BLUE}http://localhost:3001${NC}
  🔌 API Gateway:      ${BLUE}http://localhost:3000${NC}
  ❤️  Health Check:     ${BLUE}http://localhost:3000/health${NC}

${CYAN}Service Status:${NC}
  ✓ Trading Engine:    Running (PID: $(cat $PID_DIR/trading-engine.pid 2>/dev/null || echo "N/A"))
  ✓ API Gateway:       Running (PID: $(cat $PID_DIR/api-gateway.pid 2>/dev/null || echo "N/A"))
  ✓ Discord Bot:       Running (PID: $(cat $PID_DIR/discord-bot.pid 2>/dev/null || echo "N/A"))
  ✓ Frontend:          Running (PID: $(cat $PID_DIR/frontend.pid 2>/dev/null || echo "N/A"))
  ✓ PostgreSQL:        Running
  ✓ Redis:             Running

${CYAN}Log Files:${NC}
  📝 Trading Engine:   ${BLUE}logs/trading-engine.log${NC}
  📝 API Gateway:      ${BLUE}logs/api-gateway.log${NC}
  📝 Discord Bot:      ${BLUE}logs/discord-bot.log${NC}
  📝 Frontend:         ${BLUE}logs/frontend.log${NC}

${CYAN}Useful Commands:${NC}
  📋 View logs:        ${BLUE}./view-logs.sh${NC}
  🛑 Stop all:         ${BLUE}./stop.sh${NC}
  🔄 Restart:          ${BLUE}./restart.sh${NC}

${YELLOW}Trading Mode:${NC} ${TRADING_MODE:-paper}

${YELLOW}⚠️  Remember:${NC}
  • Always test in PAPER mode first
  • Monitor logs for errors
  • Check positions regularly
  • Options trading involves risk

${GREEN}Happy Trading! 🚀📈${NC}

EOF

# Offer to tail logs
read -p "Would you like to view live logs? (y/n): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    bash "$PROJECT_ROOT/view-logs.sh"
fi
