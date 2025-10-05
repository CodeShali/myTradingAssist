#!/bin/bash

#############################################################################
# Docker Status Script
# Check status of all Docker containers
#############################################################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
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
║   Trading Platform - Docker Status                           ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF

echo -e "\n${CYAN}Container Status:${NC}\n"

# Check if any containers are running
RUNNING_COUNT=$(docker ps --filter "name=trading_" --format "{{.Names}}" | wc -l)

if [ "$RUNNING_COUNT" -eq "0" ]; then
    echo -e "${YELLOW}⚠ No trading containers are running${NC}\n"
    echo -e "${BLUE}To start: ./docker-start.sh${NC}\n"
    exit 0
fi

# Show container status
docker ps --filter "name=trading_" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n${CYAN}Container Health:${NC}\n"

# Check each container
for container in trading_postgres trading_redis trading_engine api_gateway discord_bot trading_frontend; do
    if docker ps --filter "name=$container" --format "{{.Names}}" | grep -q "$container"; then
        STATUS=$(docker inspect --format='{{.State.Status}}' $container 2>/dev/null)
        HEALTH=$(docker inspect --format='{{.State.Health.Status}}' $container 2>/dev/null)
        
        if [ "$STATUS" = "running" ]; then
            if [ "$HEALTH" = "healthy" ]; then
                echo -e "  ${GREEN}✓${NC} $container is ${GREEN}running${NC} and ${GREEN}healthy${NC}"
            elif [ "$HEALTH" = "unhealthy" ]; then
                echo -e "  ${RED}✗${NC} $container is ${YELLOW}running${NC} but ${RED}unhealthy${NC}"
            else
                echo -e "  ${GREEN}✓${NC} $container is ${GREEN}running${NC}"
            fi
        else
            echo -e "  ${RED}✗${NC} $container is ${RED}$STATUS${NC}"
        fi
    else
        echo -e "  ${RED}✗${NC} $container is ${RED}not running${NC}"
    fi
done

# Check API health
echo -e "\n${CYAN}API Health:${NC}\n"

if curl -s http://localhost:3000/health >/dev/null 2>&1; then
    HEALTH_RESPONSE=$(curl -s http://localhost:3000/health)
    echo -e "  ${GREEN}✓${NC} API Gateway is ${GREEN}healthy${NC}"
    echo -e "  ${BLUE}Response:${NC} $HEALTH_RESPONSE"
else
    echo -e "  ${RED}✗${NC} API Gateway health check ${RED}failed${NC}"
fi

# Check frontend
if curl -s http://localhost:3001 >/dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Frontend is ${GREEN}accessible${NC}"
else
    echo -e "  ${RED}✗${NC} Frontend is ${RED}not accessible${NC}"
fi

# Docker resources
echo -e "\n${CYAN}Resource Usage:${NC}\n"

docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" \
    $(docker ps --filter "name=trading_" --format "{{.Names}}")

# Volume info
echo -e "\n${CYAN}Data Volumes:${NC}\n"

docker volume ls --filter "name=myTradingAssist" --format "table {{.Name}}\t{{.Driver}}"

# Recent logs
echo -e "\n${CYAN}Recent Errors (last 10):${NC}\n"

ERRORS=$($COMPOSE_CMD logs --tail=100 2>/dev/null | grep -i "error\|exception\|failed" | tail -10)

if [ -n "$ERRORS" ]; then
    echo "$ERRORS" | while read line; do
        echo -e "  ${RED}•${NC} ${line:0:100}"
    done
else
    echo -e "  ${GREEN}✓${NC} No recent errors"
fi

echo -e "\n${CYAN}Quick Actions:${NC}\n"
echo -e "  ${BLUE}./docker-start.sh${NC}      - Start all containers"
echo -e "  ${BLUE}./docker-stop.sh${NC}       - Stop all containers"
echo -e "  ${BLUE}./docker-restart.sh${NC}    - Restart all containers"
echo -e "  ${BLUE}docker compose logs -f${NC} - View live logs"
echo -e "  ${BLUE}docker compose ps${NC}      - List containers"
echo -e ""
