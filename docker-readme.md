# README-DOCKER.md

# Investment Portfolio MVP - Docker Setup Guide

## 🐳 Docker Configuration Overview

This project now supports full Docker containerization with PostgreSQL database, Redis caching, and orchestrated services.

### Key Features:
- **Multi-stage Docker builds** for optimized production images
- **PostgreSQL database** with connection pooling
- **Redis caching** for improved performance
- **Health checks** for all services
- **Environment-based configuration**
- **Automatic database initialization**
- **Development and production modes**

## 🚀 Quick Start with Docker

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 8GB+ RAM recommended
- Ports 3000, 8000, 5432, 6379 available

### 1. Clone and Setup
```bash
# Clone the repository
git clone <repository-url>
cd investment-portfolio-mvp

# Make scripts executable (Linux/Mac)
chmod +x docker-start.sh docker-stop.sh

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

### 3. Initialize Database (if not auto-initialized)
```bash
# Initialize with sample data
docker compose exec backend python scripts/init_data.py
```

### 4. Access Services
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432 (portfolio_user/portfolio_password)
- **Redis**: localhost:6379

## 🛠️ Service Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (Next.js)     │◄───┤   (FastAPI)     │◄───┤  (PostgreSQL)   │
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

## 📁 Docker Files Structure

```
investment-portfolio/
├── docker-compose.yml           # Main orchestration
├── .env                         # Environment variables
├── .env.production             # Production environment
├── docker-start.sh             # Start script
├── docker-stop.sh              # Stop script
├── init-scripts/               # Database init scripts
│   └── 01-init-database.sql
├── flexpesa-ai/
│   ├── Dockerfile              # Backend container
│   ├── requirements.txt        # Updated with PostgreSQL
│   └── app/core/config.py      # Updated configuration
└── flexpesa-client/
    ├── Dockerfile              # Frontend container
    └── src/lib/api.ts          # Updated API client
```

## 🔧 Configuration

### Environment Variables (.env)
```env
# Environment
ENVIRONMENT=development
NODE_ENV=development
DOCKER_ENV=true

# Database
POSTGRES_DB=portfolio_db
POSTGRES_USER=portfolio_user
POSTGRES_PASSWORD=portfolio_password
DATABASE_URL=postgresql://portfolio_user:portfolio_password@postgres:5432/portfolio_db

# API Keys (Optional)
NEWS_API_KEY=your_news_api_key
GEMINI_API_KEY=your_gemini_api_key

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Security
SECRET_KEY=your-secret-key-change-in-production
```

### Production Configuration (.env.production)
```env
ENVIRONMENT=production
NODE_ENV=production
DEBUG=false
POSTGRES_PASSWORD=super-secure-password
SECRET_KEY=super-secure-secret-key
ALLOWED_ORIGINS=https://yourdomain.com
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1
```

## 📋 Management Commands

### Service Management
```bash
# Start all services
./docker-start.sh

# Stop all services
./docker-stop.sh

# Restart services
./docker-start.sh restart

# View logs
./docker-start.sh logs

# Check status
./docker-start.sh status
```

### Docker Compose Commands
```bash
# Build and start services
docker compose up --build -d

# Stop services
docker compose down

# View logs
docker compose logs -f

# Execute commands in containers
docker compose exec backend python scripts/init_data.py
docker compose exec frontend npm run build
docker compose exec postgres psql -U portfolio_user -d portfolio_db

# Scale services
docker compose up --scale frontend=2 --scale backend=3
```

### Database Management
```bash
# Initialize database
docker compose exec backend python scripts/init_data.py

# Connect to database
docker compose exec postgres psql -U portfolio_user -d portfolio_db

# Database backup
docker compose exec postgres pg_dump -U portfolio_user portfolio_db > backup.sql

# Database restore
docker compose exec -T postgres psql -U portfolio_user -d portfolio_db < backup.sql

# View database logs
docker compose logs postgres
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Services Won't Start
```bash
# Check if ports are in use
netstat -tulpn | grep -E ':(3000|8000|5432|6379)'

# Free up ports
sudo lsof -ti:3000 | xargs kill -9
sudo lsof -ti:8000 | xargs kill -9
```

#### 2. Database Connection Issues
```bash
# Check database logs
docker compose logs postgres

# Test database connection
docker compose exec postgres pg_isready -U portfolio_user

# Recreate database
docker compose down -v
docker compose up -d postgres
```

#### 3. Frontend Can't Connect to Backend
```bash
# Check network connectivity
docker compose exec frontend ping backend

# Check environment variables
docker compose exec frontend env | grep API_URL

# Restart frontend service
docker compose restart frontend
```

#### 4. Out of Memory Errors
```bash
# Check Docker resource usage
docker stats

# Increase Docker memory limit (Docker Desktop)
# Settings > Resources > Advanced > Memory: 8GB+
```

### Health Checks
```bash
# Check all service health
docker compose ps

# Individual service health
curl http://localhost:8000/         # Backend
curl http://localhost:3000/         # Frontend
docker compose exec postgres pg_isready  # Database
docker compose exec redis redis-cli ping # Redis
```

### Performance Optimization
```bash
# Use build cache
docker compose build --parallel

# Prune unused images
docker image prune -a

# Clean up volumes
docker volume prune
```

## 🚀 Production Deployment

### 1. Environment Setup
```bash
# Use production environment
cp .env.production .env

# Update configuration
nano .env
```

### 2. Security Hardening
```bash
# Generate secure secret key
openssl rand -hex 32

# Use strong database password
openssl rand -base64 32

# Configure firewall (Ubuntu)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. Production Deployment
```bash
# Build for production
docker compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start production services
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Setup reverse proxy (Nginx)
# Configure SSL certificates (Let's Encrypt)
```

### 4. Monitoring & Logging
```bash
# Centralized logging
docker compose logs --since 1h -f

# Resource monitoring
docker stats --no-stream

# Health monitoring
watch 'curl -s http://localhost:8000/ | jq .status'
```

## 📊 Database Schema Migration

When updating models, use Alembic migrations:

```bash
# Generate migration
docker compose exec backend alembic revision --autogenerate -m "Add new field"

# Apply migration
docker compose exec backend alembic upgrade head

# Rollback migration
docker compose exec backend alembic downgrade -1
```

## 🔒 Security Best Practices

1. **Change default passwords** in production
2. **Use environment variables** for secrets
3. **Enable SSL/TLS** for production
4. **Regular security updates** for base images
5. **Network isolation** between services
6. **Backup encryption** for sensitive data

## 📈 Scaling & Performance

### Horizontal Scaling
```bash
# Scale backend services
docker compose up --scale backend=3 -d

# Load balancer configuration
# Use Nginx or Traefik for load balancing
```

### Vertical Scaling
```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```

### Caching Strategy
```bash
# Redis configuration for caching
# Enable caching in backend configuration
# Monitor cache hit rates
docker compose exec redis redis-cli info stats
```

## 🆘 Support

### Log Analysis
```bash
# Backend logs
docker compose logs backend | grep -i error

# Frontend logs
docker compose logs frontend | grep -i error

# Database logs
docker compose logs postgres | tail -100
```

### Health Endpoints
- Backend: http://localhost:8000/
- Frontend: http://localhost:3000/
- Database: `docker compose exec postgres pg_isready`

### Getting Help
1. Check service logs: `docker compose logs <service>`
2. Verify environment variables: `docker compose config`
3. Test network connectivity between services
4. Review resource usage: `docker stats`
5. Check official documentation for each service

---

## 📝 Notes

- **First startup** may take 2-3 minutes as images are built and database is initialized
- **PostgreSQL data** persists in Docker volumes
- **Development mode** includes hot reload for both frontend and backend
- **Health checks** ensure services are ready before dependent services start
- **Graceful shutdown** preserves data and connections when stopping services