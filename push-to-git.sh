#!/bin/bash

#############################################################################
# Git Repository Setup and Push Script
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

clear
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   Git Repository Setup                                       ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF

echo -e "\n${CYAN}This script will help you push your project to Git.${NC}\n"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}Git is not installed. Please install Git first.${NC}"
    exit 1
fi

# Step 1: Configure Git user (for this repo only)
echo -e "${CYAN}Step 1: Git User Configuration${NC}\n"

read -p "Enter your Git username: " git_username
read -p "Enter your Git email: " git_email

git config user.name "$git_username"
git config user.email "$git_email"

echo -e "${GREEN}✓ Git user configured for this repository${NC}"
echo -e "  Username: $git_username"
echo -e "  Email: $git_email\n"

# Step 2: Initialize repository (if not already)
echo -e "${CYAN}Step 2: Initialize Git Repository${NC}\n"

if [ -d ".git" ]; then
    echo -e "${YELLOW}Repository already initialized${NC}\n"
else
    git init
    echo -e "${GREEN}✓ Git repository initialized${NC}\n"
fi

# Step 3: Verify .gitignore
echo -e "${CYAN}Step 3: Verify .gitignore${NC}\n"

if [ -f ".gitignore" ]; then
    echo -e "${GREEN}✓ .gitignore file exists${NC}"
    echo -e "${YELLOW}Important files that will NOT be committed:${NC}"
    echo "  - .env (API keys and secrets)"
    echo "  - logs/ (log files)"
    echo "  - venv/ (Python virtual environment)"
    echo "  - node_modules/ (Node dependencies)"
    echo ""
else
    echo -e "${RED}✗ .gitignore file not found${NC}"
    exit 1
fi

# Step 4: Check for sensitive files
echo -e "${CYAN}Step 4: Security Check${NC}\n"

if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  WARNING: .env file exists${NC}"
    echo -e "${GREEN}✓ It will be ignored by Git (not committed)${NC}\n"
fi

# Step 5: Add files
echo -e "${CYAN}Step 5: Stage Files for Commit${NC}\n"

git add .

# Show what will be committed
echo -e "${BLUE}Files to be committed:${NC}"
git status --short | head -20
echo ""

file_count=$(git status --short | wc -l | tr -d ' ')
echo -e "${GREEN}Total files staged: $file_count${NC}\n"

# Step 6: Create initial commit
echo -e "${CYAN}Step 6: Create Initial Commit${NC}\n"

read -p "Enter commit message (or press Enter for default): " commit_message

if [ -z "$commit_message" ]; then
    commit_message="Initial commit: AI-Assisted Options Trading Platform"
fi

git commit -m "$commit_message"
echo -e "${GREEN}✓ Commit created${NC}\n"

# Step 7: Add remote repository
echo -e "${CYAN}Step 7: Add Remote Repository${NC}\n"

echo -e "${YELLOW}Choose your Git hosting service:${NC}"
echo "  1) GitHub"
echo "  2) GitLab"
echo "  3) Bitbucket"
echo "  4) Other"
echo ""

read -p "Enter choice (1-4): " hosting_choice

case $hosting_choice in
    1)
        echo -e "\n${BLUE}GitHub Setup:${NC}"
        echo "1. Go to https://github.com/new"
        echo "2. Create a new repository (e.g., 'myTradingAssist')"
        echo "3. Copy the repository URL"
        ;;
    2)
        echo -e "\n${BLUE}GitLab Setup:${NC}"
        echo "1. Go to https://gitlab.com/projects/new"
        echo "2. Create a new project"
        echo "3. Copy the repository URL"
        ;;
    3)
        echo -e "\n${BLUE}Bitbucket Setup:${NC}"
        echo "1. Go to https://bitbucket.org/repo/create"
        echo "2. Create a new repository"
        echo "3. Copy the repository URL"
        ;;
    4)
        echo -e "\n${BLUE}Other Git Service:${NC}"
        echo "Create a repository on your Git service and copy the URL"
        ;;
esac

echo ""
read -p "Enter your repository URL (e.g., https://github.com/username/repo.git): " repo_url

if [ -z "$repo_url" ]; then
    echo -e "${RED}No repository URL provided. Exiting.${NC}"
    exit 1
fi

# Check if remote already exists
if git remote | grep -q "origin"; then
    echo -e "${YELLOW}Remote 'origin' already exists. Removing...${NC}"
    git remote remove origin
fi

git remote add origin "$repo_url"
echo -e "${GREEN}✓ Remote repository added${NC}\n"

# Step 8: Push to remote
echo -e "${CYAN}Step 8: Push to Remote Repository${NC}\n"

echo -e "${YELLOW}Pushing to: $repo_url${NC}\n"

# Determine default branch name
default_branch=$(git symbolic-ref --short HEAD 2>/dev/null || echo "main")

echo -e "${BLUE}Pushing to branch: $default_branch${NC}\n"

# Push with authentication prompt
if git push -u origin "$default_branch"; then
    echo -e "\n${GREEN}✓ Successfully pushed to remote repository!${NC}\n"
    
    # Success summary
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ Repository Setup Complete!${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}\n"
    
    echo -e "${BLUE}Repository URL:${NC} $repo_url"
    echo -e "${BLUE}Branch:${NC} $default_branch"
    echo -e "${BLUE}Commits:${NC} $(git rev-list --count HEAD)"
    echo -e "${BLUE}Files:${NC} $file_count"
    
    echo -e "\n${CYAN}Next Steps:${NC}"
    echo "  1. Visit your repository: $repo_url"
    echo "  2. Add a description and topics"
    echo "  3. Set repository to private (recommended for trading bots)"
    echo "  4. Enable branch protection (optional)"
    
    echo -e "\n${YELLOW}⚠️  Security Reminder:${NC}"
    echo "  • Your .env file is NOT in the repository (it's ignored)"
    echo "  • Never commit API keys or secrets"
    echo "  • Keep your repository private"
    
    echo -e "\n${GREEN}Future Updates:${NC}"
    echo "  git add ."
    echo "  git commit -m \"Your commit message\""
    echo "  git push"
    
else
    echo -e "\n${RED}✗ Push failed${NC}\n"
    
    echo -e "${YELLOW}Common Issues:${NC}"
    echo "  1. Authentication failed - Check your credentials"
    echo "  2. Repository doesn't exist - Create it first"
    echo "  3. No permission - Check repository access"
    echo "  4. Branch protection - Disable temporarily"
    
    echo -e "\n${BLUE}Troubleshooting:${NC}"
    echo "  • For HTTPS: Use personal access token instead of password"
    echo "  • For SSH: Set up SSH keys first"
    echo "  • Check: git remote -v"
    
    echo -e "\n${CYAN}To retry:${NC}"
    echo "  ./push-to-git.sh"
fi

echo ""
