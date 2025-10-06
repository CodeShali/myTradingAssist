#!/bin/bash

#############################################################################
# Docker Restart Script
# Restart all Docker containers
#############################################################################

# Colors
CYAN='\033[0;36m'
NC='\033[0m'

# Get the actual project root (two levels up from this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

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
