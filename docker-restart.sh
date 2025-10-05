#!/bin/bash

#############################################################################
# Docker Restart Script
# Restart all Docker containers
#############################################################################

# Colors
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

clear
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   Restarting Trading Platform (Docker)                       ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF

echo -e "\n${CYAN}Stopping containers...${NC}\n"
bash "$PROJECT_ROOT/docker-stop.sh"

echo -e "\n${CYAN}Starting containers...${NC}\n"
sleep 2
bash "$PROJECT_ROOT/docker-start.sh"
