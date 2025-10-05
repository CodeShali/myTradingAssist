#!/bin/bash

#############################################################################
# Log Viewer Script
# View logs from all services in a unified interface
#############################################################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$PROJECT_ROOT/logs"

clear
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   Trading Platform - Log Viewer                              ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF

echo -e "\n${CYAN}Select log to view:${NC}\n"

echo "  1) All logs (combined)"
echo "  2) Trading Engine"
echo "  3) API Gateway"
echo "  4) Discord Bot"
echo "  5) Frontend"
echo "  6) Errors only (all services)"
echo "  7) Live tail (all logs)"
echo "  8) Custom filter"
echo "  9) Exit"

echo -e "\n"
read -p "Enter choice (1-9): " choice

case $choice in
    1)
        echo -e "\n${CYAN}Showing all logs (last 100 lines):${NC}\n"
        for log in trading-engine api-gateway discord-bot frontend; do
            if [ -f "$LOG_DIR/${log}.log" ]; then
                echo -e "${MAGENTA}=== $log ===${NC}"
                tail -n 25 "$LOG_DIR/${log}.log"
                echo ""
            fi
        done
        ;;
    2)
        echo -e "\n${CYAN}Trading Engine Logs:${NC}\n"
        if [ -f "$LOG_DIR/trading-engine.log" ]; then
            tail -f "$LOG_DIR/trading-engine.log"
        else
            echo -e "${RED}Log file not found${NC}"
        fi
        ;;
    3)
        echo -e "\n${CYAN}API Gateway Logs:${NC}\n"
        if [ -f "$LOG_DIR/api-gateway.log" ]; then
            tail -f "$LOG_DIR/api-gateway.log"
        else
            echo -e "${RED}Log file not found${NC}"
        fi
        ;;
    4)
        echo -e "\n${CYAN}Discord Bot Logs:${NC}\n"
        if [ -f "$LOG_DIR/discord-bot.log" ]; then
            tail -f "$LOG_DIR/discord-bot.log"
        else
            echo -e "${RED}Log file not found${NC}"
        fi
        ;;
    5)
        echo -e "\n${CYAN}Frontend Logs:${NC}\n"
        if [ -f "$LOG_DIR/frontend.log" ]; then
            tail -f "$LOG_DIR/frontend.log"
        else
            echo -e "${RED}Log file not found${NC}"
        fi
        ;;
    6)
        echo -e "\n${CYAN}Error Logs (all services):${NC}\n"
        grep -i "error\|exception\|failed" "$LOG_DIR"/*.log 2>/dev/null | tail -n 50
        ;;
    7)
        echo -e "\n${CYAN}Live tail (all logs):${NC}\n"
        echo -e "${YELLOW}Press Ctrl+C to stop${NC}\n"
        tail -f "$LOG_DIR"/*.log 2>/dev/null
        ;;
    8)
        read -p "Enter search term: " search_term
        echo -e "\n${CYAN}Searching for: $search_term${NC}\n"
        grep -i "$search_term" "$LOG_DIR"/*.log 2>/dev/null | tail -n 50
        ;;
    9)
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac
