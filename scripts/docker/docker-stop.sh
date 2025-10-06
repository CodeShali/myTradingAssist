#!/bin/bash

#############################################################################
# Docker Stop Script
# Gracefully stop all Docker containers
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
cd "$PROJECT_ROOT"

# Detect compose command
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

clear
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   Stopping Trading Platform (Docker)                         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF

echo -e "\n${YELLOW}Stopping all containers...${NC}\n"

# Stop containers
if $COMPOSE_CMD down; then
    echo -e "\n${GREEN}✓ All containers stopped${NC}"
    echo -e "${BLUE}Data is preserved in Docker volumes${NC}\n"
else
    echo -e "\n${RED}✗ Failed to stop some containers${NC}\n"
    exit 1
fi

# Show remaining containers
REMAINING=$(docker ps --filter "name=trading_" --format "{{.Names}}" | wc -l)

if [ "$REMAINING" -eq "0" ]; then
    echo -e "${GREEN}✓ All trading containers stopped${NC}\n"
else
    echo -e "${YELLOW}⚠ $REMAINING container(s) still running${NC}"
    docker ps --filter "name=trading_"
    echo ""
fi
