#!/bin/bash

#############################################################################
# Stop Script
# Gracefully stop all trading platform services
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
║   Stopping Trading Platform                                  ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF

echo -e "\n${YELLOW}Stopping all services...${NC}\n"

# Function to stop service
stop_service() {
    local name=$1
    local pid_file="$PID_DIR/${name}.pid"
    
    if [ -f "$pid_file" ]; then
        PID=$(cat "$pid_file")
        
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "${BLUE}Stopping $name (PID: $PID)...${NC}"
            kill $PID 2>/dev/null
            
            # Wait for graceful shutdown
            for i in {1..10}; do
                if ! ps -p $PID > /dev/null 2>&1; then
                    echo -e "${GREEN}✓ $name stopped${NC}"
                    rm -f "$pid_file"
                    return 0
                fi
                sleep 1
            done
            
            # Force kill if still running
            if ps -p $PID > /dev/null 2>&1; then
                echo -e "${YELLOW}Force stopping $name...${NC}"
                kill -9 $PID 2>/dev/null
                sleep 1
            fi
            
            echo -e "${GREEN}✓ $name stopped${NC}"
            rm -f "$pid_file"
        else
            echo -e "${YELLOW}⚠ $name is not running${NC}"
            rm -f "$pid_file"
        fi
    else
        echo -e "${YELLOW}⚠ No PID file for $name${NC}"
    fi
}

# Stop services in reverse order
stop_service "frontend"
stop_service "discord-bot"
stop_service "api-gateway"
stop_service "trading-engine"

# Optional: Stop Redis if started by script
read -p "Stop Redis? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v redis-cli >/dev/null 2>&1; then
        redis-cli shutdown 2>/dev/null
        echo -e "${GREEN}✓ Redis stopped${NC}"
    fi
fi

echo -e "\n${GREEN}✓ All services stopped${NC}"
echo -e "${BLUE}Logs are preserved in: logs/${NC}\n"
