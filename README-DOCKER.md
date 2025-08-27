# Investment Portfolio MVP - Docker Setup Guide (PostgreSQL Only)

## 🐳 Docker Configuration Overview

This project uses **PostgreSQL ONLY** for all database operations with full Docker containerization, Redis caching, and orchestrated services.

### Key Features:
- **PostgreSQL database** with connection pooling and optimized settings
- **Redis caching** for improved performance
- **Multi-stage Docker builds** for optimized production images
- **Health checks** for all services
- **Environment-based configuration**
- **Automatic database initialization**

## 🚀 Quick Start with Docker

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 8GB+ RAM recommended
- Ports 3000, 8000, 5432, 6379 available

### 1. Clone and Setup
```bash
git clone <repository-url>
cd investment-portfolio-mvp

# Make scripts executable (Linux/Mac)
chmod +x docker-start.sh docker-stop.sh remove-sqlite.sh

# Copy environment file
cp .env.example .env
```

### 2. Start All Services
```bash
# Option 1: Use the convenience script
./docker-start.sh

# Option 2: Use docker compose directly
docker compose up --build -d
```

### 3. Initialize PostgreSQL Database
```bash
# Initialize with sample data
docker compose exec backend python scripts/init_data.py
```

### 4. Access Services
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL Database**: localhost:5432 (portfolio_user/portfolio_password)
- **Redis**: localhost:6379

## 🛠️ Service Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   PostgreSQL    │
│   (Next.js)     │◄───┤   (FastAPI)     │◄───┤   Database      │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                        ┌─────────────────┐
                        │     Redis       │
                        │   (Cache)       │
                        │   Port: 6379    │
                        └─────────────────┘
```

## 📊 PostgreSQL Features

- **Connection Pooling**: Optimized for concurrent connections
- **Health Monitoring**: Automatic health checks and recovery
- **Backup Support**: Built-in backup and restore capabilities
- **Performance Tuning**: Optimized PostgreSQL settings
- **ACID Compliance**: Full transaction support
- **Scalability**: Ready for production workloads

## 🔧 PostgreSQL Management

### Database Commands
```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U portfolio_user -d portfolio_db

# Database backup
docker compose exec postgres pg_dump -U portfolio_user portfolio_db > backup.sql

# Database restore
docker compose exec -T postgres psql -U portfolio_user -d portfolio_db < backup.sql

# Check database status
docker compose exec postgres pg_isready -U portfolio_user
```

### Performance Monitoring
```bash
# Check connection pool status
curl -s http://localhost:8000/api/v1/database/pool-status

# Database performance metrics
docker compose exec postgres psql -U portfolio_user -d portfolio_db -c "SELECT * FROM pg_stat_activity;"
```

This setup provides enterprise-grade PostgreSQL functionality with full Docker orchestration for development and production use.
