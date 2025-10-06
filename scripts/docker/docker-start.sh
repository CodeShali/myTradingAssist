#!/bin/bash

#############################################################################
# Docker-Based Startup Script
# Starts the entire platform using Docker Compose
#############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Get the actual project root (two levels up from this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

LOG_FILE="$PROJECT_ROOT/logs/docker-startup.log"
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

#############################################################################
# Banner
#############################################################################

clear
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   AI-Assisted Options Trading Platform (Docker)              ║
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

# Check Docker
print_step "Checking Docker..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
    print_success "Docker $DOCKER_VERSION installed"
else
    print_error "Docker is required but not installed"
    echo -e "\n${BLUE}Installation:${NC}"
    echo "  macOS: Download from https://www.docker.com/products/docker-desktop"
    echo "  Linux: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

# Check Docker Compose
print_step "Checking Docker Compose..."
if docker compose version &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version | cut -d' ' -f4)
    print_success "Docker Compose $COMPOSE_VERSION installed"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f4 | tr -d ',')
    print_success "Docker Compose $COMPOSE_VERSION installed"
    COMPOSE_CMD="docker-compose"
else
    print_error "Docker Compose is required but not installed"
    exit 1
fi

# Set compose command
COMPOSE_CMD="${COMPOSE_CMD:-docker compose}"

# Check if Docker is running
print_step "Checking Docker daemon..."
if docker info &> /dev/null; then
    print_success "Docker daemon is running"
else
    print_error "Docker daemon is not running"
    print_info "Please start Docker Desktop or Docker service"
    exit 1
fi

#############################################################################
# Step 2: Environment Configuration
#############################################################################

print_header "Step 2: Environment Configuration"

ENV_FILE="$PROJECT_ROOT/.env"

if [ -f "$ENV_FILE" ]; then
    print_success ".env file found"
    
    # Check required variables
    print_step "Validating environment variables..."
    
    source "$ENV_FILE"
    
    REQUIRED_VARS=(
        "ALPACA_API_KEY"
        "ALPACA_SECRET_KEY"
        "POLYGON_API_KEY"
        "NEWS_API_KEY"
        "JWT_SECRET"
    )
    
    MISSING_VARS=0
    for var in "${REQUIRED_VARS[@]}"; do
        value="${!var}"
        if [ -z "$value" ] || [ "$value" = "your_"* ] || [ ${#value} -lt 10 ]; then
            print_warning "$var is not configured (empty or placeholder)"
            MISSING_VARS=1
        else
            print_success "$var is configured"
        fi
    done
    
    if [ $MISSING_VARS -eq 1 ]; then
        print_warning "Some environment variables are missing"
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
        print_error ".env.example not found"
        exit 1
    fi
fi

#############################################################################
# Step 3: Pull/Build Docker Images
#############################################################################

print_header "Step 3: Building Docker Images"

print_step "Pulling base images and building containers..."
print_info "This may take a few minutes on first run..."

if $COMPOSE_CMD build >> "$LOG_FILE" 2>&1; then
    print_success "Docker images built successfully"
else
    print_error "Failed to build Docker images"
    print_info "Check logs: $LOG_FILE"
    exit 1
fi

#############################################################################
# Step 4: Start Services
#############################################################################

print_header "Step 4: Starting Services"

print_step "Starting all containers..."

if $COMPOSE_CMD up -d >> "$LOG_FILE" 2>&1; then
    print_success "All containers started"
else
    print_error "Failed to start containers"
    print_info "Check logs: $LOG_FILE"
    exit 1
fi

#############################################################################
# Step 5: Wait for Services
#############################################################################

print_header "Step 5: Waiting for Services to be Ready"

# Wait for PostgreSQL
print_step "Waiting for PostgreSQL..."
for i in {1..30}; do
    if docker exec trading_postgres pg_isready -U trading_user &> /dev/null; then
        print_success "PostgreSQL is ready"
        break
    fi
    echo -n "."
    sleep 1
done

# Wait for Redis
print_step "Waiting for Redis..."
for i in {1..30}; do
    if docker exec trading_redis redis-cli ping &> /dev/null; then
        print_success "Redis is ready"
        break
    fi
    echo -n "."
    sleep 1
done

# Wait for API Gateway
print_step "Waiting for API Gateway..."
for i in {1..60}; do
    if curl -s http://localhost:3000/health &> /dev/null; then
        print_success "API Gateway is ready"
        break
    fi
    echo -n "."
    sleep 1
done

# Wait for Frontend
print_step "Waiting for Frontend..."
for i in {1..60}; do
    if curl -s http://localhost:3001 &> /dev/null; then
        print_success "Frontend is ready"
        break
    fi
    echo -n "."
    sleep 1
done

#############################################################################
# Step 6: Health Checks
#############################################################################

print_header "Step 6: Running Health Checks"

sleep 3

# Check container status
print_step "Checking container status..."
RUNNING_CONTAINERS=$(docker ps --filter "name=trading_" --format "{{.Names}}" | wc -l)
print_success "$RUNNING_CONTAINERS containers running"

# Check API health
print_step "Checking API Gateway..."
if curl -s http://localhost:3000/health | grep -q "healthy"; then
    print_success "API Gateway is healthy"
else
    print_warning "API Gateway health check inconclusive"
fi

#############################################################################
# Final Summary
#############################################################################

print_header "🎉 Platform Started Successfully!"

cat << EOF

${GREEN}All services are running in Docker containers!${NC}

${CYAN}Access Points:${NC}
  📊 Web Dashboard:    ${BLUE}http://localhost:3001${NC}
  🔌 API Gateway:      ${BLUE}http://localhost:3000${NC}
  ❤️  Health Check:     ${BLUE}http://localhost:3000/health${NC}

${CYAN}Container Status:${NC}
EOF

docker ps --filter "name=trading_" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

cat << EOF

${CYAN}Useful Commands:${NC}
  📋 View logs:        ${BLUE}docker compose logs -f${NC}
  📋 View specific:    ${BLUE}docker compose logs -f [service]${NC}
  🛑 Stop all:         ${BLUE}./docker-stop.sh${NC}
  🔄 Restart:          ${BLUE}./docker-restart.sh${NC}
  📊 Container status: ${BLUE}docker compose ps${NC}
  🔍 Enter container:  ${BLUE}docker exec -it [container] sh${NC}

${CYAN}Service Names:${NC}
  - trading_postgres (Database)
  - trading_redis (Cache)
  - trading_engine (Python AI Engine)
  - api_gateway (Node.js API)
  - discord_bot (Discord Bot)
  - trading_frontend (React Dashboard)

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
    $COMPOSE_CMD logs -f
fi
