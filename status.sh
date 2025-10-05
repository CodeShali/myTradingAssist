#!/bin/bash

#############################################################################
# Status Check Script
# Check the status of all platform services
#############################################################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_DIR="$PROJECT_ROOT/logs/pids"

clear
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   Trading Platform - Status Check                            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF

echo -e "\n${CYAN}Service Status:${NC}\n"

# Function to check service status
check_service() {
    local name=$1
    local pid_file="$PID_DIR/${name}.pid"
    local port=$2
    
    if [ -f "$pid_file" ]; then
        PID=$(cat "$pid_file")
        
        if ps -p $PID > /dev/null 2>&1; then
            if [ -n "$port" ] && lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
                echo -e "  ${GREEN}✓${NC} $name is ${GREEN}running${NC} (PID: $PID, Port: $port)"
                return 0
            elif [ -z "$port" ]; then
                echo -e "  ${GREEN}✓${NC} $name is ${GREEN}running${NC} (PID: $PID)"
                return 0
            else
                echo -e "  ${YELLOW}⚠${NC} $name process exists but port $port not listening (PID: $PID)"
                return 1
            fi
        else
            echo -e "  ${RED}✗${NC} $name is ${RED}stopped${NC} (stale PID file)"
            return 1
        fi
    else
        echo -e "  ${RED}✗${NC} $name is ${RED}stopped${NC}"
        return 1
    fi
}

# Check all services
check_service "trading-engine"
check_service "api-gateway" 3000
check_service "discord-bot"
check_service "frontend" 3001

echo -e "\n${CYAN}Infrastructure Status:${NC}\n"

# Check PostgreSQL
if command -v pg_isready >/dev/null 2>&1; then
    if pg_isready >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} PostgreSQL is ${GREEN}running${NC}"
    else
        echo -e "  ${RED}✗${NC} PostgreSQL is ${RED}not running${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠${NC} PostgreSQL status unknown (pg_isready not found)"
fi

# Check Redis
if command -v redis-cli >/dev/null 2>&1; then
    if redis-cli ping >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Redis is ${GREEN}running${NC}"
    else
        echo -e "  ${RED}✗${NC} Redis is ${RED}not running${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠${NC} Redis status unknown (redis-cli not found)"
fi

# Check API health
echo -e "\n${CYAN}API Health:${NC}\n"

if curl -s http://localhost:3000/health >/dev/null 2>&1; then
    HEALTH=$(curl -s http://localhost:3000/health)
    echo -e "  ${GREEN}✓${NC} API Gateway is ${GREEN}healthy${NC}"
    echo -e "  ${BLUE}Response:${NC} $HEALTH"
else
    echo -e "  ${RED}✗${NC} API Gateway health check ${RED}failed${NC}"
fi

# Check database connection
echo -e "\n${CYAN}Database Connection:${NC}\n"

if [ -f "$PROJECT_ROOT/.env" ]; then
    source "$PROJECT_ROOT/.env"
    
    if psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM users" >/dev/null 2>&1; then
        USER_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM users" 2>/dev/null | tr -d ' ')
        echo -e "  ${GREEN}✓${NC} Database is ${GREEN}accessible${NC}"
        echo -e "  ${BLUE}Users:${NC} $USER_COUNT"
    else
        echo -e "  ${RED}✗${NC} Database connection ${RED}failed${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠${NC} .env file not found"
fi

# Port usage
echo -e "\n${CYAN}Port Usage:${NC}\n"

PORTS=(3000 3001 5432 6379)
PORT_NAMES=("API Gateway" "Frontend" "PostgreSQL" "Redis")

for i in "${!PORTS[@]}"; do
    PORT=${PORTS[$i]}
    NAME=${PORT_NAMES[$i]}
    
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        PID=$(lsof -ti:$PORT)
        echo -e "  ${GREEN}✓${NC} Port $PORT ($NAME) - ${GREEN}in use${NC} by PID $PID"
    else
        echo -e "  ${YELLOW}○${NC} Port $PORT ($NAME) - ${YELLOW}available${NC}"
    fi
done

# Disk usage
echo -e "\n${CYAN}Disk Usage:${NC}\n"

LOG_SIZE=$(du -sh "$PROJECT_ROOT/logs" 2>/dev/null | cut -f1)
echo -e "  ${BLUE}Logs:${NC} $LOG_SIZE"

# Recent errors
echo -e "\n${CYAN}Recent Errors (last 5):${NC}\n"

if ls "$PROJECT_ROOT/logs"/*.log >/dev/null 2>&1; then
    ERRORS=$(grep -i "error\|exception" "$PROJECT_ROOT/logs"/*.log 2>/dev/null | tail -n 5)
    
    if [ -n "$ERRORS" ]; then
        echo "$ERRORS" | while read line; do
            echo -e "  ${RED}•${NC} ${line:0:100}"
        done
    else
        echo -e "  ${GREEN}✓${NC} No recent errors"
    fi
else
    echo -e "  ${YELLOW}⚠${NC} No log files found"
fi

# Trading mode
if [ -f "$PROJECT_ROOT/.env" ]; then
    source "$PROJECT_ROOT/.env"
    echo -e "\n${CYAN}Configuration:${NC}\n"
    echo -e "  ${BLUE}Trading Mode:${NC} ${TRADING_MODE:-not set}"
    
    if [ "$TRADING_MODE" = "live" ]; then
        echo -e "  ${RED}⚠️  LIVE TRADING MODE - Real money at risk!${NC}"
    else
        echo -e "  ${GREEN}✓ Paper trading mode${NC}"
    fi
fi

echo -e "\n${CYAN}Quick Actions:${NC}\n"
echo -e "  ${BLUE}./start.sh${NC}      - Start all services"
echo -e "  ${BLUE}./stop.sh${NC}       - Stop all services"
echo -e "  ${BLUE}./restart.sh${NC}    - Restart all services"
echo -e "  ${BLUE}./view-logs.sh${NC}  - View logs"
echo -e ""
