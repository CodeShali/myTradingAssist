#!/bin/bash

#############################################################################
# Final Cleanup and Start Script for OptionsAI
# Cleans up, organizes, and starts the complete platform
#############################################################################

set -e

PROJECT_ROOT="/Users/shashank/Documents/myTradingAssist"
cd "$PROJECT_ROOT"

echo "🧹 OptionsAI - Final Cleanup and Setup"
echo "========================================"
echo ""

# Step 1: Clean up temporary and duplicate files
echo "📁 Step 1: Cleaning up temporary files..."

# Remove temporary frontend directories
if [ -d "frontend-temp" ]; then
    echo "  Removing frontend-temp..."
    rm -rf frontend-temp
fi

# Remove duplicate/old documentation
echo "  Cleaning up duplicate documentation..."
rm -f CREATE_FULL_FRONTEND.md
rm -f COMPLETE_FRONTEND_READY.md
rm -f FRONTEND_COMPLETE_GUIDE.md
rm -f FRONTEND_STATUS.md
rm -f build-frontend.sh
rm -f generate-frontend.sh
rm -f generate-remaining-frontend.sh
rm -f setup-frontend-complete.sh
rm -f SETUP_FRONTEND_TEMPLATE.md

echo "✅ Cleanup complete!"
echo ""

# Step 2: Replace old frontend with new one
echo "📦 Step 2: Setting up frontend..."

if [ -d "frontend-new" ] && [ -d "frontend-new/src" ]; then
    echo "  Backing up old frontend..."
    if [ -d "frontend" ]; then
        mv frontend frontend-backup-$(date +%Y%m%d-%H%M%S)
    fi
    
    echo "  Installing new frontend..."
    mv frontend-new frontend
    
    echo "✅ Frontend updated!"
else
    echo "⚠️  frontend-new not found or incomplete"
fi

echo ""

# Step 3: Create .env file if missing
echo "⚙️  Step 3: Checking configuration..."

if [ ! -f ".env" ]; then
    echo "  Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please run: ./setup-env.sh to configure API keys"
else
    echo "✅ .env file exists"
fi

echo ""

# Step 4: Summary
echo "📊 Step 4: Project Summary"
echo "=========================="
echo ""
echo "Frontend: $([ -d "frontend/src" ] && echo "✅ Ready" || echo "❌ Missing")"
echo "Backend:  $([ -d "backend/trading_engine" ] && echo "✅ Ready" || echo "❌ Missing")"
echo "Database: $([ -d "database/migrations" ] && echo "✅ Ready" || echo "❌ Missing")"
echo ".env:     $([ -f ".env" ] && echo "✅ Exists" || echo "❌ Missing")"
echo "Docker:   $(docker --version > /dev/null 2>&1 && echo "✅ Installed" || echo "❌ Not installed")"
echo ""

# Step 5: Next steps
echo "🚀 Next Steps:"
echo "=============="
echo ""
echo "1. Configure API keys (if not done):"
echo "   ./setup-env.sh"
echo ""
echo "2. Start the platform:"
echo "   ./start.sh"
echo ""
echo "3. Or start with Docker:"
echo "   docker compose up -d"
echo ""
echo "✅ Cleanup complete! Ready to start."
