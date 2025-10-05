#!/bin/bash

#############################################################################
# Smart Start Script - Auto-detects Docker or Manual Setup
#############################################################################

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

clear
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   AI-Assisted Options Trading Platform                       ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF

echo -e "\n${CYAN}Detecting setup method...${NC}\n"

# Check if Docker is available
if command -v docker &> /dev/null && docker info &> /dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker detected and running${NC}"
    echo -e "${BLUE}Using Docker setup (recommended)${NC}\n"
    
    # Check if docker-compose is available
    if docker compose version &> /dev/null 2>&1 || command -v docker-compose &> /dev/null 2>&1; then
        echo -e "${CYAN}Starting platform with Docker...${NC}\n"
        exec bash "$PROJECT_ROOT/docker-start.sh"
    else
        echo -e "${YELLOW}Docker Compose not found${NC}"
        echo -e "${BLUE}Please install Docker Compose${NC}\n"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ Docker not detected or not running${NC}"
    echo -e "${BLUE}Using manual setup${NC}\n"
    
    # Check if prerequisites are installed
    MISSING=0
    
    if ! command -v psql &> /dev/null; then
        echo -e "${YELLOW}✗ PostgreSQL not found${NC}"
        MISSING=1
    fi
    
    if ! command -v redis-cli &> /dev/null; then
        echo -e "${YELLOW}✗ Redis not found${NC}"
        MISSING=1
    fi
    
    if [ $MISSING -eq 1 ]; then
        echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${CYAN}Recommendation: Use Docker Setup${NC}"
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
        
        echo -e "${GREEN}Docker setup is easier:${NC}"
        echo -e "  1. Install Docker Desktop: ${BLUE}https://www.docker.com/products/docker-desktop${NC}"
        echo -e "  2. Run: ${BLUE}./start.sh${NC}"
        echo -e "  3. Done! No PostgreSQL/Redis installation needed\n"
        
        echo -e "${YELLOW}Or install prerequisites manually:${NC}"
        echo -e "  macOS: ${BLUE}brew install postgresql redis${NC}"
        echo -e "  Linux: ${BLUE}sudo apt install postgresql redis-server${NC}\n"
        
        read -p "Continue with manual setup anyway? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    echo -e "${CYAN}Starting platform with manual setup...${NC}\n"
    exec bash "$PROJECT_ROOT/manual-start.sh"
fi
