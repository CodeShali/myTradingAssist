# Trading Platform Scripts Guide

This directory contains convenient shell scripts to manage the AI-Assisted Options Trading Platform.

## 🚀 Quick Start

```bash
# First time setup
./setup-env.sh    # Configure environment variables
./start.sh        # Start all services

# Daily usage
./status.sh       # Check service status
./view-logs.sh    # View logs
./stop.sh         # Stop all services
./restart.sh      # Restart all services
```

## 📜 Script Reference

### `start.sh` - Main Startup Script

**Purpose**: Complete platform startup with health checks and validation

**What it does**:
1. ✅ Checks all prerequisites (Python, Node.js, PostgreSQL, Redis)
2. ✅ Validates environment configuration
3. ✅ Sets up database (creates tables if needed)
4. ✅ Installs dependencies (if not already installed)
5. ✅ Checks port availability
6. ✅ Starts all services in background
7. ✅ Runs health checks
8. ✅ Displays status and access points

**Usage**:
```bash
./start.sh
```

**Output**:
- Colored status messages for each step
- Service PIDs and ports
- Access URLs for web dashboard and API
- Log file locations
- Option to view live logs

**Logs**: `logs/startup.log`

---

### `setup-env.sh` - Environment Configuration Wizard

**Purpose**: Interactive setup for environment variables

**What it does**:
1. Prompts for all required API keys
2. Generates secure random secrets
3. Configures database connection
4. Sets trading parameters
5. Creates `.env` file with proper permissions

**Usage**:
```bash
./setup-env.sh
```

**Required Information**:
- Alpaca API credentials
- Polygon.io API key
- NewsAPI key
- Discord bot token
- PostgreSQL password
- Trading mode (paper/live)
- Risk parameters

**Security**:
- Hides sensitive input (passwords, secrets)
- Sets restrictive file permissions (600)
- Generates cryptographically secure random keys

---

### `status.sh` - Service Status Checker

**Purpose**: Quick health check of all platform components

**What it displays**:
- ✓ Service status (running/stopped)
- ✓ Process IDs and ports
- ✓ PostgreSQL connection
- ✓ Redis connection
- ✓ API health endpoint
- ✓ Database connectivity
- ✓ Port usage
- ✓ Disk usage
- ✓ Recent errors
- ✓ Trading mode

**Usage**:
```bash
./status.sh
```

**Example Output**:
```
Service Status:
  ✓ trading-engine is running (PID: 12345)
  ✓ api-gateway is running (PID: 12346, Port: 3000)
  ✓ discord-bot is running (PID: 12347)
  ✓ frontend is running (PID: 12348, Port: 3001)

Infrastructure Status:
  ✓ PostgreSQL is running
  ✓ Redis is running

API Health:
  ✓ API Gateway is healthy
```

---

### `view-logs.sh` - Log Viewer

**Purpose**: Unified log viewing interface

**Options**:
1. **All logs (combined)** - Last 25 lines from each service
2. **Trading Engine** - Live tail of trading engine logs
3. **API Gateway** - Live tail of API logs
4. **Discord Bot** - Live tail of Discord bot logs
5. **Frontend** - Live tail of frontend logs
6. **Errors only** - Last 50 error messages from all services
7. **Live tail (all)** - Real-time view of all logs
8. **Custom filter** - Search logs for specific terms
9. **Exit**

**Usage**:
```bash
./view-logs.sh
```

**Keyboard Shortcuts**:
- `Ctrl+C` - Stop tailing logs
- `q` - Quit less viewer

**Log Locations**:
- `logs/trading-engine.log`
- `logs/api-gateway.log`
- `logs/discord-bot.log`
- `logs/frontend.log`
- `logs/startup.log`

---

### `stop.sh` - Graceful Shutdown

**Purpose**: Stop all platform services safely

**What it does**:
1. Stops frontend
2. Stops Discord bot
3. Stops API gateway
4. Stops trading engine
5. Optionally stops Redis
6. Cleans up PID files
7. Preserves all logs

**Usage**:
```bash
./stop.sh
```

**Shutdown Process**:
- Sends SIGTERM for graceful shutdown
- Waits up to 10 seconds per service
- Force kills (SIGKILL) if necessary
- Removes stale PID files

**Note**: Logs are preserved in `logs/` directory

---

### `restart.sh` - Quick Restart

**Purpose**: Stop and restart all services

**What it does**:
1. Calls `stop.sh` to stop all services
2. Waits 2 seconds
3. Calls `start.sh` to restart everything

**Usage**:
```bash
./restart.sh
```

**Use Cases**:
- After configuration changes
- After code updates
- To clear stuck processes
- To apply new environment variables

---

## 🔧 Common Tasks

### First Time Setup

```bash
# 1. Configure environment
./setup-env.sh

# 2. Start platform
./start.sh

# 3. Check status
./status.sh
```

### Daily Operations

```bash
# Start trading day
./start.sh

# Monitor activity
./view-logs.sh    # Select option 7 for live tail

# Check status
./status.sh

# End trading day
./stop.sh
```

### Troubleshooting

```bash
# Check what's wrong
./status.sh

# View error logs
./view-logs.sh    # Select option 6

# Restart everything
./restart.sh

# View specific service logs
./view-logs.sh    # Select specific service
```

### After Configuration Changes

```bash
# Update .env file manually or run:
./setup-env.sh

# Restart to apply changes
./restart.sh
```

### Monitoring Performance

```bash
# Real-time logs
./view-logs.sh    # Option 7

# Check for errors
./view-logs.sh    # Option 6

# Search for specific events
./view-logs.sh    # Option 8, then enter search term
```

## 📊 Log Files

All logs are stored in the `logs/` directory:

| File | Description | Rotation |
|------|-------------|----------|
| `startup.log` | Platform startup messages | Manual cleanup |
| `trading-engine.log` | Trading engine activity | 100MB / 30 days |
| `api-gateway.log` | API requests and responses | 5MB / 5 files |
| `discord-bot.log` | Discord bot activity | 5MB / 5 files |
| `frontend.log` | Frontend build and errors | 5MB / 5 files |
| `pids/*.pid` | Process ID files | Auto-cleanup |

## 🔐 Security Notes

### File Permissions

Scripts automatically set secure permissions:
- `.env` file: `600` (owner read/write only)
- Shell scripts: `755` (executable by all, writable by owner)

### Sensitive Data

Never commit these files to version control:
- `.env` - Contains API keys and secrets
- `logs/*.log` - May contain sensitive trading data
- `logs/pids/*.pid` - Runtime process information

### API Keys

The `setup-env.sh` script:
- Hides password input
- Generates cryptographically secure random secrets
- Warns about live trading mode
- Validates required fields

## 🐛 Troubleshooting

### "Permission denied" when running scripts

```bash
chmod +x *.sh
```

### Services won't start

```bash
# Check prerequisites
./status.sh

# Check logs for errors
./view-logs.sh

# Verify .env configuration
cat .env | grep -v "SECRET\|PASSWORD\|KEY"
```

### Port already in use

```bash
# Check what's using the port
lsof -i :3000
lsof -i :3001

# Kill the process
kill -9 <PID>

# Or let start.sh handle it
./start.sh  # It will prompt to kill processes
```

### Database connection errors

```bash
# Check PostgreSQL is running
pg_isready

# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Check DATABASE_URL in .env
grep DATABASE_URL .env
```

### Redis connection errors

```bash
# Check Redis is running
redis-cli ping

# Start Redis
redis-server --daemonize yes

# Check REDIS_URL in .env
grep REDIS_URL .env
```

### Python virtual environment issues

```bash
# Remove and recreate
rm -rf backend/trading_engine/venv
./start.sh  # Will recreate automatically
```

### Node modules issues

```bash
# Clear and reinstall
rm -rf backend/*/node_modules
rm -rf frontend/node_modules
./start.sh  # Will reinstall automatically
```

## 📈 Performance Tips

### Reduce Log Size

```bash
# Clean old logs
find logs -name "*.log" -mtime +30 -delete

# Compress old logs
gzip logs/*.log.old
```

### Monitor Resource Usage

```bash
# Check process resources
ps aux | grep -E "python|node"

# Check disk usage
du -sh logs/
```

### Optimize Startup Time

- Keep dependencies installed (don't delete node_modules)
- Use SSD for database
- Increase PostgreSQL shared_buffers
- Use Redis persistence (AOF) for faster restarts

## 🆘 Getting Help

1. **Check Status**: `./status.sh`
2. **View Logs**: `./view-logs.sh`
3. **Search Errors**: `./view-logs.sh` → Option 6
4. **Check Documentation**: See `README.md` and `SETUP_GUIDE.md`
5. **Review Configuration**: `cat .env` (hide secrets!)

## 🔄 Update Workflow

After pulling code updates:

```bash
# 1. Stop services
./stop.sh

# 2. Update dependencies
cd backend/trading_engine && source venv/bin/activate && pip install -r requirements.txt
cd ../api_gateway && npm install
cd ../discord_bot && npm install
cd ../../frontend && npm install

# 3. Run migrations (if any)
psql $DATABASE_URL -f database/migrations/XXX_new_migration.sql

# 4. Restart
./start.sh
```

## 📝 Script Customization

All scripts support customization through environment variables:

```bash
# Custom log directory
export LOG_DIR=/custom/path/logs
./start.sh

# Custom PID directory
export PID_DIR=/custom/path/pids
./start.sh

# Skip health checks
export SKIP_HEALTH_CHECKS=true
./start.sh
```

---

**Happy Trading! 🚀📈**

For more information, see:
- [Main README](README.md)
- [Setup Guide](SETUP_GUIDE.md)
- [Architecture](ARCHITECTURE.md)
