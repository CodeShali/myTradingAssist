# 🐳 Docker Quick Start Guide

## Why Docker?

✅ **No manual installation** of PostgreSQL, Redis, Python, or Node.js
✅ **Consistent environment** across all systems
✅ **Easy cleanup** - just delete containers
✅ **Isolated** - doesn't affect your system
✅ **Production-ready** - same setup for dev and prod

---

## Prerequisites

### 1. Install Docker Desktop

**macOS:**
1. Download from https://www.docker.com/products/docker-desktop
2. Install and start Docker Desktop
3. Verify: `docker --version`

**Linux:**
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Log out and back in
```

**Windows:**
1. Download from https://www.docker.com/products/docker-desktop
2. Install Docker Desktop
3. Enable WSL 2 backend

### 2. Verify Installation

```bash
docker --version
docker compose version
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Configure Environment

```bash
cd /Users/shashank/Documents/myTradingAssist

# Run the setup wizard
./setup-env.sh
```

Enter your API keys when prompted.

### Step 2: Start Everything

```bash
# Start all containers
./docker-start.sh
```

This will:
- Pull Docker images (first time only)
- Build your application containers
- Start PostgreSQL, Redis, and all services
- Run health checks
- Show you the status

**Wait for:** "🎉 Platform Started Successfully!"

### Step 3: Access the Platform

- **Web Dashboard**: http://localhost:3001
- **API**: http://localhost:3000

---

## 📋 Common Commands

### Start/Stop/Restart

```bash
./docker-start.sh      # Start all containers
./docker-stop.sh       # Stop all containers
./docker-restart.sh    # Restart all containers
./docker-status.sh     # Check status
```

### View Logs

```bash
# All logs
docker compose logs -f

# Specific service
docker compose logs -f trading_engine
docker compose logs -f api_gateway
docker compose logs -f discord_bot
docker compose logs -f frontend

# Last 100 lines
docker compose logs --tail=100
```

### Container Management

```bash
# List running containers
docker compose ps

# Enter a container
docker exec -it trading_engine sh
docker exec -it api_gateway sh
docker exec -it trading_postgres sh

# Restart a specific service
docker compose restart trading_engine

# View resource usage
docker stats
```

### Database Access

```bash
# Connect to PostgreSQL
docker exec -it trading_postgres psql -U trading_user -d trading_platform

# Run SQL query
docker exec -it trading_postgres psql -U trading_user -d trading_platform -c "SELECT * FROM users;"

# Backup database
docker exec trading_postgres pg_dump -U trading_user trading_platform > backup.sql

# Restore database
cat backup.sql | docker exec -i trading_postgres psql -U trading_user trading_platform
```

### Redis Access

```bash
# Connect to Redis
docker exec -it trading_redis redis-cli

# Check keys
docker exec -it trading_redis redis-cli KEYS '*'

# Get a value
docker exec -it trading_redis redis-cli GET some_key
```

---

## 🔧 Troubleshooting

### Containers Won't Start

```bash
# Check Docker is running
docker info

# Check logs for errors
docker compose logs

# Rebuild containers
docker compose build --no-cache
docker compose up -d
```

### Port Already in Use

```bash
# Find what's using the port
lsof -i :3000
lsof -i :3001
lsof -i :5432

# Kill the process
kill -9 <PID>

# Or change ports in docker-compose.yml
```

### Database Connection Errors

```bash
# Check PostgreSQL is running
docker compose ps postgres

# Check PostgreSQL logs
docker compose logs postgres

# Restart PostgreSQL
docker compose restart postgres
```

### Out of Disk Space

```bash
# Clean up unused Docker resources
docker system prune -a

# Remove old volumes (WARNING: deletes data)
docker volume prune
```

### Reset Everything

```bash
# Stop and remove all containers and volumes
docker compose down -v

# Rebuild from scratch
./docker-start.sh
```

---

## 📊 What's Running?

### Containers

| Container | Purpose | Port |
|-----------|---------|------|
| trading_postgres | PostgreSQL Database | 5432 |
| trading_redis | Redis Cache | 6379 |
| trading_engine | Python AI Engine | - |
| api_gateway | Node.js API | 3000 |
| discord_bot | Discord Bot | - |
| trading_frontend | React Dashboard | 3001 |

### Volumes

| Volume | Purpose |
|--------|---------|
| postgres_data | Database files |
| redis_data | Redis persistence |

### Network

All containers communicate on the `trading_network` Docker network.

---

## 🔄 Update Workflow

### Update Code

```bash
# Pull latest code
git pull

# Rebuild containers
docker compose build

# Restart
./docker-restart.sh
```

### Update Dependencies

```bash
# Python dependencies
docker compose build trading_engine

# Node.js dependencies
docker compose build api_gateway discord_bot frontend

# Restart
./docker-restart.sh
```

### Database Migrations

```bash
# Run migration
docker exec -it trading_postgres psql -U trading_user -d trading_platform -f /docker-entrypoint-initdb.d/002_new_migration.sql
```

---

## 🎯 Development Tips

### Live Code Reload

The containers are configured to reload automatically when you change code (for development).

### Access Container Shell

```bash
# Python environment
docker exec -it trading_engine sh

# Node.js environment
docker exec -it api_gateway sh

# Database
docker exec -it trading_postgres sh
```

### View Environment Variables

```bash
docker exec trading_engine env
docker exec api_gateway env
```

### Copy Files

```bash
# From container to host
docker cp trading_engine:/app/logs/trading.log ./local-logs/

# From host to container
docker cp ./config.py trading_engine:/app/
```

---

## 🚨 Important Notes

### Data Persistence

- Database data is stored in Docker volumes
- Logs are stored in `./logs` directory on your host
- Data persists even when containers are stopped

### Stopping vs Removing

```bash
# Stop (data preserved)
docker compose stop

# Remove (data preserved in volumes)
docker compose down

# Remove with volumes (data deleted!)
docker compose down -v
```

### Resource Limits

Docker Desktop has resource limits. If containers are slow:

1. Open Docker Desktop
2. Go to Settings → Resources
3. Increase CPU and Memory
4. Apply & Restart

---

## 📈 Production Deployment

### Build for Production

```bash
# Build optimized images
docker compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start in production mode
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Environment Variables

For production, use a separate `.env.production` file:

```bash
cp .env .env.production
# Edit .env.production with production values

# Use it
docker compose --env-file .env.production up -d
```

---

## 🆘 Getting Help

### Check Status

```bash
./docker-status.sh
```

### View Logs

```bash
docker compose logs -f
```

### Container Not Starting?

```bash
# Check specific container logs
docker compose logs [container_name]

# Check if port is in use
lsof -i :[port]

# Rebuild container
docker compose build [container_name]
docker compose up -d [container_name]
```

---

## ✨ Advantages of Docker Setup

✅ **No PostgreSQL/Redis installation needed**
✅ **Consistent across all environments**
✅ **Easy to reset and start fresh**
✅ **Isolated from your system**
✅ **Production-ready**
✅ **Easy to scale**
✅ **Simple backup/restore**

---

## 🎉 You're Ready!

```bash
# Start everything
./docker-start.sh

# Check status
./docker-status.sh

# View logs
docker compose logs -f

# Stop when done
./docker-stop.sh
```

**Happy Trading! 🚀📈**
