#!/bin/bash

#############################################################################
# Project Reorganization Script
# Cleans up and organizes the entire project structure
#############################################################################

set -e

PROJECT_ROOT="/Users/shashank/Documents/myTradingAssist"
cd "$PROJECT_ROOT"

echo "🧹 OptionsAI - Complete Project Reorganization"
echo "=============================================="
echo ""

# Create organized directory structure
echo "📁 Creating organized directory structure..."
mkdir -p docs/{guides,reference,api}
mkdir -p scripts/{docker,manual,setup}
mkdir -p archive

echo "✅ Directories created"
echo ""

# Move documentation to docs/
echo "📚 Organizing documentation..."

# Main docs
mv README.md docs/ 2>/dev/null || true
mv ARCHITECTURE.md docs/reference/ 2>/dev/null || true
mv PROJECT_SUMMARY.md docs/reference/ 2>/dev/null || true

# Guides
mv START_HERE.md docs/ 2>/dev/null || true
mv DOCKER_QUICKSTART.md docs/guides/ 2>/dev/null || true
mv SETUP_GUIDE.md docs/guides/ 2>/dev/null || true
mv API_KEYS_GUIDE.md docs/guides/ 2>/dev/null || true
mv CHECKLIST.md docs/guides/ 2>/dev/null || true

# Archive old/duplicate docs
mv ALL_QUESTIONS_ANSWERED.md archive/ 2>/dev/null || true
mv CLEANUP_SUMMARY.md archive/ 2>/dev/null || true
mv COMPLETE_PLATFORM_READY.md archive/ 2>/dev/null || true
mv CONFIGURATION_EXPLAINED.md archive/ 2>/dev/null || true
mv DOCKER_SETUP_COMPLETE.md archive/ 2>/dev/null || true
mv FILES_EXPLAINED.md archive/ 2>/dev/null || true
mv FINAL_CLEANUP_AND_START.sh archive/ 2>/dev/null || true
mv FINAL_STATUS.md archive/ 2>/dev/null || true
mv FRONTEND_COMPLETE.md archive/ 2>/dev/null || true
mv GET_STARTED.md archive/ 2>/dev/null || true
mv INDEX.md archive/ 2>/dev/null || true
mv QUESTIONS_ANSWERED.md archive/ 2>/dev/null || true
mv QUICKSTART.md archive/ 2>/dev/null || true
mv README_FINAL.md archive/ 2>/dev/null || true
mv SCRIPTS_README.md archive/ 2>/dev/null || true

echo "✅ Documentation organized"
echo ""

# Move scripts to scripts/
echo "📜 Organizing scripts..."

# Docker scripts
mv docker-start.sh scripts/docker/ 2>/dev/null || true
mv docker-stop.sh scripts/docker/ 2>/dev/null || true
mv docker-restart.sh scripts/docker/ 2>/dev/null || true
mv docker-status.sh scripts/docker/ 2>/dev/null || true

# Manual scripts
mv manual-start.sh scripts/manual/ 2>/dev/null || true
mv manual-stop.sh scripts/manual/ 2>/dev/null || true
mv manual-restart.sh scripts/manual/ 2>/dev/null || true
mv manual-status.sh scripts/manual/ 2>/dev/null || true
mv manual-view-logs.sh scripts/manual/ 2>/dev/null || true

# Setup scripts
mv setup-env.sh scripts/setup/ 2>/dev/null || true
mv push-to-git.sh scripts/setup/ 2>/dev/null || true

echo "✅ Scripts organized"
echo ""

# Remove backup folders
echo "🗑️  Removing backup folders..."
rm -rf frontend-backup-* 2>/dev/null || true

echo "✅ Backups removed"
echo ""

# Create new main scripts in root
echo "📝 Creating main scripts in root..."

# Main start script
cat > start.sh << 'EOFSTART'
#!/bin/bash
# Main start script - delegates to Docker or manual
exec bash scripts/docker/docker-start.sh
EOFSTART

# Main stop script
cat > stop.sh << 'EOFSTOP'
#!/bin/bash
# Main stop script
exec bash scripts/docker/docker-stop.sh
EOFSTOP

# Status script
cat > status.sh << 'EOFSTATUS'
#!/bin/bash
# Status check script
exec bash scripts/docker/docker-status.sh
EOFSTATUS

# Setup script
cat > setup.sh << 'EOFSETUP'
#!/bin/bash
# Setup script
exec bash scripts/setup/setup-env.sh
EOFSETUP

chmod +x start.sh stop.sh status.sh setup.sh

echo "✅ Main scripts created"
echo ""

# Create simple README
cat > README.md << 'EOFREADME'
# OptionsAI - AI-Assisted Options Trading Platform

## 🚀 Quick Start

```bash
# 1. Configure
./setup.sh

# 2. Start
./start.sh

# 3. Access
open http://localhost:3001
```

## 📚 Documentation

See `docs/START_HERE.md` for complete guide.

## 🎯 Features

- AI-powered signal generation
- Multi-channel confirmation (Discord + Web)
- Real-time position tracking
- Automated risk management
- NLP-based updates (optional)

## ⚠️ Disclaimer

Options trading involves substantial risk. Always start in PAPER TRADING mode.

---

**Full documentation:** `docs/`
EOFREADME

echo "✅ New README created"
echo ""

# Create docs index
cat > docs/INDEX.md << 'EOFDOCS'
# OptionsAI Documentation

## 📖 Start Here
- **[START_HERE.md](START_HERE.md)** - 10-minute quick start

## 📚 Guides
- **[guides/DOCKER_QUICKSTART.md](guides/DOCKER_QUICKSTART.md)** - Docker setup
- **[guides/API_KEYS_GUIDE.md](guides/API_KEYS_GUIDE.md)** - API configuration
- **[guides/SETUP_GUIDE.md](guides/SETUP_GUIDE.md)** - Detailed setup
- **[guides/CHECKLIST.md](guides/CHECKLIST.md)** - Pre-trading checklist

## 🔍 Reference
- **[reference/ARCHITECTURE.md](reference/ARCHITECTURE.md)** - System design
- **[reference/PROJECT_SUMMARY.md](reference/PROJECT_SUMMARY.md)** - Overview

## 🎯 Quick Commands

```bash
./setup.sh    # Configure
./start.sh    # Start
./stop.sh     # Stop
./status.sh   # Check status
```
EOFDOCS

echo "✅ Documentation index created"
echo ""

echo "🎉 Reorganization Complete!"
echo "=========================="
echo ""
echo "📁 New Structure:"
echo "  ├── README.md              (Simple overview)"
echo "  ├── setup.sh               (Configure API keys)"
echo "  ├── start.sh               (Start platform)"
echo "  ├── stop.sh                (Stop platform)"
echo "  ├── status.sh              (Check status)"
echo "  ├── docs/                  (All documentation)"
echo "  │   ├── START_HERE.md"
echo "  │   ├── guides/"
echo "  │   └── reference/"
echo "  ├── scripts/               (All scripts)"
echo "  │   ├── docker/"
echo "  │   ├── manual/"
echo "  │   └── setup/"
echo "  ├── backend/               (Backend code)"
echo "  ├── frontend/              (Frontend code)"
echo "  ├── database/              (Database schemas)"
echo "  └── archive/               (Old files)"
echo ""
echo "✅ Project is now clean and organized!"
echo ""
echo "🚀 Next steps:"
echo "  1. ./setup.sh    (Configure API keys)"
echo "  2. ./start.sh    (Start platform)"
echo ""
