**Minimal .env configuration:**

```env
# Environment
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=postgresql://portfolio_user:portfolio_password@localhost:5432/portfolio_db

# Security
SECRET_KEY=your-secret-key-change-in-production

# Authentication (Optional - can disable for development)
DISABLE_AUTH=true
CLERK_SECRET_KEY=your-clerk-secret-key
CLERK_PUBLISHABLE_KEY=your-clerk-publishable-key

# AI Services (Optional but recommended)
NEWS_API_KEY=your-news-api-key
GEMINI_API_KEY=your-gemini-api-key

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

### 4. Initialize Database

```bash
# Initialize with comprehensive demo data
python scripts/init_data.py

# Or for production (minimal data)
python scripts/init_production_db.py
```

### 5. Start the Server

```bash
# Development server with auto-reload
python run.py

# Or directly with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**🎉 API will be running at:** http://localhost:8000

**📚 Interactive Documentation:** http://localhost:8000/docs

---

## 📖 API Documentation

### Core Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/` | API information and health status | ❌ |
| `GET` | `/health` | Detailed health check | ❌ |
| `GET` | `/api/v1/portfolio/summary` | **Main endpoint** - Complete portfolio overview | ✅ |
| `POST` | `/api/v1/portfolio/update-prices` | Update real-time prices for all assets | ✅ |
| `GET` | `/api/v1/accounts/` | List all user's investment accounts | ✅ |
| `POST` | `/api/v1/accounts/` | Create new investment account | ✅ |
| `POST` | `/api/v1/assets/` | Add asset to an account | ✅ |
| `POST` | `/api/v1/analysis/quick` | Quick AI analysis for specific symbols | ✅ |
| `POST` | `/api/v1/analysis/asset/{symbol}` | Enhanced AI analysis for specific asset | ✅ |

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/auth/config` | Get authentication configuration |
| `GET` | `/api/v1/auth/profile` | Get current user profile |
| `POST` | `/api/v1/auth/cookie/login` | Login with email/password |
| `POST` | `/api/v1/auth/register` | Register new user |
| `POST` | `/api/v1/auth/cookie/logout` | Logout current user |

### Performance Tracking Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/portfolios/performance` | Get performance for all portfolios |
| `GET` | `/api/v1/portfolios/performance/summary` | Portfolio performance summary |
| `GET` | `/api/v1/portfolios/{id}/performance` | Specific portfolio performance |
| `POST` | `/api/v1/portfolios/` | Create portfolio with performance tracking |
| `PUT` | `/api/v1/portfolios/{id}/performance` | Update portfolio |
| `DELETE` | `/api/v1/portfolios/{id}/performance` | Delete portfolio |

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

## 🗄️ Database Schema

### Core Models

#### Account Model
```python
class Account:
    id: int                      # Primary key
    clerk_user_id: str          # User authentication ID
    name: str                   # "Wells Fargo", "Fidelity 401k"
    account_type: str           # "brokerage", "retirement", "crypto"
    balance: float              # Calculated from assets
    description: str            # Optional description
    currency: str               # "USD", "EUR", etc.
    is_active: bool             # Soft delete flag
    created_at: datetime
    updated_at: datetime

    # Relationships
    assets: List[Asset]         # One-to-many
```

#### Asset Model
```python
class Asset:
    id: int                     # Primary key
    account_id: int             # Foreign key to Account
    symbol: str                 # "AAPL", "BTC-USD", etc.
    name: str                   # Full company/asset name
    shares: float               # Number of shares/units owned
    avg_cost: float             # Average cost per share
    current_price: float        # Latest market price
    asset_type: str             # "stock", "crypto", "etf"
    sector: str                 # "Technology", "Healthcare"
    industry: str               # "Software", "Pharmaceuticals"
    currency: str               # "USD"
    exchange: str               # "NYSE", "NASDAQ"
    is_active: bool             # Active position flag
    created_at: datetime
    last_updated: datetime
    price_updated_at: datetime
```

#### Market Data Cache
```python
class MarketData:
    symbol: str                 # Unique symbol identifier
    name: str                   # Full security name
    current_price: float        # Latest price
    day_change: float           # Daily change in dollars
    day_change_percent: float   # Daily change percentage
    volume: float               # Trading volume
    market_cap: float           # Market capitalization
    sector: str                 # Sector classification
    industry: str               # Industry classification
    updated_at: datetime        # Cache timestamp
```

#### Portfolio Snapshots
```python
class PortfolioSnapshot:
    clerk_user_id: str          # User identifier
    total_value: float          # Portfolio value at snapshot
    total_cost_basis: float     # Total cost basis
    total_pnl: float            # Profit/loss amount
    total_pnl_percent: float    # Profit/loss percentage
    asset_count: int            # Number of assets
    account_count: int          # Number of accounts
    snapshot_type: str          # "daily", "weekly", "monthly"
    created_at: datetime
```

---

## 🔧 Configuration Guide

### Environment Variables

#### Core Settings
```env
# Application Environment
ENVIRONMENT=development|staging|production
DEBUG=true|false
PROJECT_NAME="Investment Portfolio API"
API_V1_STR="/api/v1"
VERSION="1.0.0"

# Server Configuration
HOST=0.0.0.0
BACKEND_PORT=8000
```

#### Database Configuration
```env
# PostgreSQL (Production)
DATABASE_URL=postgresql://user:password@host:port/database

# Connection Pool Settings
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

#### Authentication Settings
```env
# Disable auth for development
DISABLE_AUTH=true

# Mock user for development
MOCK_USER_ID=dev_user_12345
MOCK_USER_EMAIL=dev@example.com
MOCK_USER_FIRST_NAME=Dev
MOCK_USER_LAST_NAME=User

# Clerk Authentication (Production)
CLERK_SECRET_KEY=sk_live_your_secret_key
CLERK_PUBLISHABLE_KEY=pk_live_your_publishable_key
CLERK_DOMAIN=your-domain.clerk.accounts.dev
```

#### External Services
```env
# News API for sentiment analysis
NEWS_API_KEY=your_news_api_key

# Google Gemini for AI analysis
GEMINI_API_KEY=your_gemini_api_key
```

#### Security & CORS
```env
# Security
SECRET_KEY=your-very-secure-secret-key

# CORS Origins (comma-separated)
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=100
DISABLE_RATE_LIMITING=false
```

---

## 🏗️ Development Workflow

### 1. Development Server

```bash
# Start with auto-reload
python run.py

# Or with specific settings
uvicorn app.main:app \
  --reload \
  --host 0.0.0.0 \
  --port 8000 \
  --log-level debug
```

### 2. Database Operations

```bash
# Reinitialize with fresh demo data
python scripts/init_data.py --clear-existing

# Create database migrations
python scripts/create_migration.py

# Run migrations
python scripts/migrate_db.py

# Migrate to Clerk authentication
python scripts/migrate_to_clerk.py
```

### 3. Testing the API

```bash
# Check server status
curl http://localhost:8000/

# Get portfolio summary
curl http://localhost:8000/api/v1/portfolio/summary

# Update prices
curl -X POST http://localhost:8000/api/v1/portfolio/update-prices

# Create account
curl -X POST http://localhost:8000/api/v1/accounts/ \
  -H "Content-Type: application/json" \
  -d '{"name": "My Account", "account_type": "brokerage"}'
```

### 4. Authentication Toggle

```bash
# Disable authentication for development
python scripts/toggle_auth.py off

# Enable authentication
python scripts/toggle_auth.py on

# Check current status
python scripts/toggle_auth.py status
```

---

## 🧪 Testing

### Run All Tests

```bash
# Install test dependencies
pip install -r tests/requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest tests/test_database.py  # Database tests
pytest tests/test_api.py       # API endpoint tests
pytest tests/test_services.py  # Service layer tests
pytest tests/test_health.py    # Health check tests
```

### Test Categories

#### Database Tests
- Account and asset CRUD operations
- Relationship testing
- Data integrity validation
- Transaction handling

#### API Tests
- Endpoint functionality
- Authentication flows
- Error handling
- Request/response validation

#### Service Tests
- Portfolio service operations
- Market data integration
- AI analysis functionality
- Multi-user data isolation

#### Integration Tests
- Complete workflow testing
- Cross-service functionality
- Real database scenarios

---

## 🚀 Production Deployment

### Docker Deployment

```bash
# Build production image
docker build -t portfolio-api .

# Run with environment variables
docker run -d \
  --name portfolio-api \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e CLERK_SECRET_KEY=your_key \
  -e ENVIRONMENT=production \
  portfolio-api
```

### Docker Compose

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://portfolio_user:portfolio_password@postgres:5432/portfolio_db
      - ENVIRONMENT=production
      - CLERK_SECRET_KEY=${CLERK_SECRET_KEY}
    depends_on:
      - postgres

  postgres:
    image: postgres:14
    environment:
      - POSTGRES_DB=portfolio_db
      - POSTGRES_USER=portfolio_user
      - POSTGRES_PASSWORD=portfolio_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### Environment Setup

```bash
# Production initialization
python scripts/init_production_db.py

# Validate production configuration
python -c "from app.core.config import validate_production_config; validate_production_config()"

# Run with Gunicorn
gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --max-requests 1000 \
  --timeout 120
```

---

## 🔧 Database Management

### Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1

# View migration history
alembic history
```

### Backup and Restore

```bash
# Create backup
pg_dump portfolio_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
psql portfolio_db < backup_20241201_143000.sql

# Database maintenance
psql portfolio_db -c "VACUUM ANALYZE;"
```

### Data Management

```bash
# Clean up old market data
python -c "
from app.services.market_data import MarketDataService
from app.core.database import SessionLocal
db = SessionLocal()
service = MarketDataService(db)
service.cleanup_stale_data(max_age_days=30)
"

# Create portfolio snapshots
python -c "
from app.services.portfolio_service import PortfolioService
from app.core.database import SessionLocal
db = SessionLocal()
service = PortfolioService(db)
# Create snapshots for all users
"
```

---

## 🤖 AI and Market Data

### Market Data Integration

The API integrates with multiple data sources:

- **Yahoo Finance (yfinance)** - Real-time stock and crypto prices
- **News API** - Financial news for sentiment analysis
- **Google Gemini** - Advanced AI analysis (optional)

### AI Analysis Features

#### Portfolio Analysis
```python
# Example response
{
  "recommendation": "HOLD",
  "confidence": 0.8,
  "risk_score": 3.2,
  "diversity_score": 0.7,
  "insights": [
    "Portfolio is well diversified across 4 accounts",
    "Technology sector exposure is 35%",
    "Consider rebalancing toward international markets"
  ]
}
```

#### Asset Analysis
```python
# Individual asset analysis
{
  "symbol": "AAPL",
  "recommendation": "BUY",
  "technical": {
    "rsi": 45.2,
    "rsi_signal": "NEUTRAL",
    "momentum": 5.7,
    "trend": "BULLISH"
  },
  "sentiment": {
    "score": 0.3,
    "signal": "BULLISH",
    "confidence": 0.75,
    "news_count": 12
  }
}
```

### Configuration

```env
# Enable all AI features
NEWS_API_KEY=your_news_api_key      # Required for sentiment
GEMINI_API_KEY=your_gemini_key      # Optional for enhanced analysis

# Market data settings
MARKET_DATA_UPDATE_INTERVAL=300     # 5 minutes
MARKET_DATA_BATCH_SIZE=10          # Batch size for API calls
```

---

## 🔐 Authentication & Security

### Clerk Integration

```env
# Production Clerk setup
CLERK_SECRET_KEY=sk_live_...
CLERK_PUBLISHABLE_KEY=pk_live_...
CLERK_DOMAIN=your-app.clerk.accounts.dev
```

### Development Mode

```env
# Disable authentication for development
DISABLE_AUTH=true
MOCK_USER_ID=dev_user_123
MOCK_USER_EMAIL=dev@example.com
```

### Security Features

- **JWT Token Validation** - Secure API access
- **Rate Limiting** - Configurable request limits
- **CORS Protection** - Origin-based access control
- **SQL Injection Prevention** - Parameterized queries
- **User Data Isolation** - Complete separation between users

---

## 📊 Monitoring & Health Checks

### Health Endpoints

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health with database status
curl http://localhost:8000/health/detailed

# API configuration info
curl http://localhost:8000/
```

### Metrics and Logging

```python
# Built-in business logging
from app.middleware.logging import business_logger

# Log portfolio operations
business_logger.log_portfolio_update(
    user_id="user_123",
    portfolio_value=50000.00,
    assets_updated=15
)

# Log market data fetches
business_logger.log_market_data_fetch(
    symbols=["AAPL", "MSFT"],
    success_count=2,
    duration=1.5
)
```

### Production Monitoring

```bash
# Check database connections
curl http://localhost:8000/metrics

# Monitor API performance
tail -f logs/business.log

# Database performance
psql portfolio_db -c "
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY total_time DESC LIMIT 10;
"
```

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. Database Connection Failed

```bash
# Check PostgreSQL is running
ps aux | grep postgres

# Test connection
psql postgresql://portfolio_user:portfolio_password@localhost:5432/portfolio_db

# Check configuration
python -c "from app.core.config import settings; print(settings.DATABASE_URL)"
```

#### 2. Authentication Issues

```bash
# Check authentication status
python scripts/toggle_auth.py status

# Disable auth for debugging
python scripts/toggle_auth.py off

# Verify Clerk configuration
curl http://localhost:8000/api/v1/auth/config
```

#### 3. Market Data Not Updating

```bash
# Test market data manually
python -c "
import yfinance as yf
ticker = yf.Ticker('AAPL')
print(ticker.info['regularMarketPrice'])
"

# Check API rate limits
curl http://localhost:8000/api/v1/market/status
```

#### 4. Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

#### 5. Dependencies Issues

```bash
# Recreate virtual environment
deactivate
rm -rf venv/
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Debug Mode

```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=debug

# Start with verbose output
python run.py

# Or with uvicorn
uvicorn app.main:app --log-level debug --reload
```

### Performance Issues

```bash
# Check database performance
python -c "
from app.core.database import check_database_connection
print('DB Status:', check_database_connection())
"

# Monitor API response times
curl -w '@-' http://localhost:8000/api/v1/portfolio/summary <<< "
time_total: %{time_total}
time_namelookup: %{time_namelookup}
time_connect: %{time_connect}
"
```

---

## 📦 Project Structure

```
flexpesa-ai/
├── 📁 app/                          # Main application package
│   ├── 🐍 main.py                   # FastAPI application entry point
│   ├── 📁 api/                      # API routes and endpoints
│   │   ├── 🐍 routes.py             # Main API routes
│   │   └── 🐍 auth_routes.py        # Authentication routes
│   ├── 📁 core/                     # Core application configuration
│   │   ├── 🐍 config.py             # Settings and configuration
│   │   ├── 🐍 database.py           # Database setup and connection
│   │   └── 🐍 auth.py               # Authentication configuration
│   ├── 📁 models/                   # SQLAlchemy database models
│   │   ├── 🐍 portfolio.py          # Portfolio-related models
│   │   └── 🐍 user.py               # User authentication models
│   ├── 📁 schemas/                  # Pydantic request/response schemas
│   │   └── 🐍 portfolio.py          # Portfolio data validation
│   ├── 📁 services/                 # Business logic layer
│   │   ├── 🐍 portfolio_service.py  # Core portfolio operations
│   │   ├── 🐍 market_data.py        # Market data integration
│   │   ├── 🐍 enhanced_ai.py        # AI analysis service
│   │   └── 🐍 perfomance.py         # Performance calculations
│   ├── 📁 middleware/               # Custom middleware
│   │   ├── 🐍 clerk_auth.py         # Clerk authentication
│   │   ├── 🐍 conditional_auth.py   # Auth switching logic
│   │   ├── 🐍 rate_limit.py         # Rate limiting
│   │   └── 🐍 logging.py            # Request/response logging
│   └── 📁 utils/                    # Utility functions
├── 📁 scripts/                      # Database and setup scripts
│   ├── 🐍 init_data.py              # Initialize with demo data
│   ├── 🐍 init_production_db.py     # Production database setup
│   ├── 🐍 migrate_to_clerk.py       # Clerk migration script
│   └── 🐍 toggle_auth.py            # Authentication toggle utility
├── 📁 tests/                        # Comprehensive test suite
│   ├── 🐍 test_database.py          # Database operation tests
│   ├── 🐍 test_api.py               # API endpoint tests
│   ├── 🐍 test_services.py          # Service layer tests
│   └── 🐍 test_health.py            # Health check tests
├── 📁 alembic/                      # Database migrations
│   ├── 📁 versions/                 # Migration files
│   └── 🐍 env.py                    # Alembic configuration
├── 🐳 Dockerfile                    # Container configuration
├── 🐳 docker-compose.yml            # Multi-service setup
├── ⚙️ requirements.txt              # Python dependencies
├── ⚙️ alembic.ini                   # Alembic configuration
├── 🐍 run.py                        # Development server runner
└── 📖 README.md                     # This documentation
```

---

## 🤝 Contributing

### Development Setup

```bash
# Fork and clone the repository
git clone <your-fork-url>
cd flexpesa-ai

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
pytest
python scripts/toggle_auth.py off
python run.py

# Commit and push
git add .
git commit -m "Add your feature"
git push origin feature/your-feature-name
```

### Code Standards

- **Python**: Follow PEP 8 style guidelines
- **Type Hints**: Use comprehensive type annotations
- **Testing**: Maintain >80% test coverage
- **Documentation**: Update docstrings and README
- **Security**: Follow OWASP guidelines

### Pull Request Process

1. **Update Tests** - Add tests for new features
2. **Update Documentation** - Keep README and docstrings current
3. **Test Coverage** - Ensure all tests pass
4. **Security Review** - Check for security implications
5. **Performance** - Consider impact on API performance

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

### Getting Help

- **📖 Documentation**: Check this README and `/docs` endpoint
- **🐛 Issues**: Create issues for bugs and feature requests
- **💬 Discussions**: Use GitHub Discussions for questions
- **📧 Contact**: Reach out to the development team

### Useful Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **PostgreSQL Documentation**: https://postgresql.org/docs
- **Clerk Authentication**: https://clerk.dev/docs
- **SQLAlchemy ORM**: https://sqlalchemy.org
- **Pydantic Validation**: https://pydantic.dev

---

## 🔄 Changelog

### v1.0.0 (Current)
- ✅ Complete portfolio management system
- ✅ Real-time market data integration
- ✅ AI-powered analysis and recommendations
- ✅ Clerk authentication with development mode
- ✅ PostgreSQL database with migrations
- ✅ Comprehensive test suite
- ✅ Docker containerization
- ✅ Performance tracking and analytics

### Upcoming Features
- 🔄 Advanced charting and visualization
- 🔄 Automated rebalancing suggestions
- 🔄 Tax loss harvesting analysis
- 🔄 Social trading features
- 🔄 Mobile API optimizations

---

**🚀 Happy Trading!** 📈