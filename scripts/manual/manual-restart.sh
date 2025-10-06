#!/bin/bash

#############################################################################
# Restart Script
# Stop and restart all trading platform services
#############################################################################

# Colors
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

clear
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   Restarting Trading Platform                                ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF

echo -e "\n${CYAN}Stopping services...${NC}\n"
bash "$PROJECT_ROOT/stop.sh"

echo -e "\n${CYAN}Starting services...${NC}\n"
sleep 2
bash "$PROJECT_ROOT/start.sh"
