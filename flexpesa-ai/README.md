# Investment Portfolio API - FastAPI Backend

A RESTful API for investment portfolio management with real-time market data, AI analysis, and multi-account support.

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** - [Download here](https://python.org/downloads/)
- **pip** (comes with Python)

### Setup & Run

```bash
# 1. Navigate to backend directory
cd flexpesa-ai/

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 5. Initialize database with sample data
python scripts/init_data.py

# 6. Start the API server
python run.py
```

**API will be running at:** http://localhost:8000

## 📊 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information and available endpoints |
| `GET` | `/api/v1/portfolio/summary` | **Main endpoint** - Complete portfolio overview |
| `POST` | `/api/v1/portfolio/update-prices` | Update real-time prices for all assets |
| `GET` | `/api/v1/accounts/` | List all investment accounts |
| `POST` | `/api/v1/accounts/` | Create new investment account |
| `POST` | `/api/v1/assets/` | Add asset to an account |
| `POST` | `/api/v1/analysis/quick` | Quick AI analysis for specific symbols |

### Documentation

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🗂️ Project Structure

```
flexpesa-ai/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py           # API route definitions
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Application configuration
│   │   └── database.py         # Database setup and connection
│   ├── models/
│   │   ├── __init__.py
│   │   └── portfolio.py        # SQLAlchemy database models
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── portfolio.py        # Pydantic request/response schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── portfolio_service.py # Core business logic
│   │   ├── market_data.py      # Real market data via yfinance
│   │   └── simple_ai.py        # AI analysis service
│   └── utils/
│       └── __init__.py
├── scripts/
│   └── init_data.py            # Database initialization script
├── data/
│   └── portfolioPostgreSQL            # PostgreSQL database (created automatically)
├── requirements.txt            # Python dependencies
├── run.py                      # Development server runner
└── README.md                   # This file
```

## 💾 Database Schema

### Account Model
```python
class Account:
    id: int (Primary Key)
    name: str                   # "Wells Fargo", "Stack Well", etc.
    account_type: str           # "brokerage", "retirement", etc.
    balance: float              # Calculated from assets
    created_at: datetime
    assets: List[Asset]         # One-to-many relationship
```

### Asset Model
```python
class Asset:
    id: int (Primary Key)
    account_id: int (Foreign Key)
    symbol: str                 # "AAPL", "BTC-USD", etc.
    shares: float               # Number of shares/units owned
    avg_cost: float             # Average cost per share
    current_price: float        # Latest market price
    last_updated: datetime      # Price update timestamp
```

## 📈 Sample Data

The `init_data.py` script creates sample accounts with realistic portfolio data:

### Wells Fargo Intuitive (Brokerage)
- **AAPL**: 50 shares @ $155.30 avg cost
- **MSFT**: 25 shares @ $285.20 avg cost  
- **SPY**: 15 shares @ $420.50 avg cost

### Stack Well (Investment)
- **QQQ**: 30 shares @ $350.25 avg cost
- **VTI**: 40 shares @ $220.15 avg cost
- **NVDA**: 5 shares @ $520.80 avg cost

### Cash App Investing (Trading)
- **TSLA**: 8 shares @ $180.45 avg cost
- **AMD**: 25 shares @ $85.60 avg cost
- **GOOGL**: 12 shares @ $125.30 avg cost

### Robinhood (Crypto)
- **BTC-USD**: 0.5 units @ $35,000 avg cost
- **ETH-USD**: 2.5 units @ $2,200 avg cost

**Total Portfolio Value**: ~$139,230 (with current market prices)

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `flexpesa-ai/` directory:

```env
# Database
DATABASE_URL=postgresql:///./data/portfolioPostgreSQL

# Optional: News API for sentiment analysis
NEWS_API_KEY=your_news_api_key_here

# Optional: Custom configuration
PROJECT_NAME=Investment Portfolio MVP
API_V1_STR=/api/v1
```

### Settings (app/core/config.py)

```python
class Settings:
    PROJECT_NAME: str = "Investment Portfolio MVP"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = "postgresql:///./data/portfolioPostgreSQL"
    NEWS_API_KEY: Optional[str] = None  # For AI sentiment analysis
```

## 📦 Dependencies

### Core Dependencies
- **FastAPI**: Modern web framework for building APIs
- **SQLAlchemy**: Database ORM for Python
- **Pydantic**: Data validation using Python type hints
- **Uvicorn**: ASGI server for running the application

### Data & Finance
- **yfinance**: Real-time market data from Yahoo Finance
- **pandas**: Data manipulation and analysis
- **requests**: HTTP library for API calls

### Development
- **pydantic-settings**: Settings management

### Full Requirements (requirements.txt)
```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
pandas==2.1.4
yfinance==0.2.28
pydantic-settings==2.1.0
```

## 🔄 Development Workflow

### 1. Start Development Server
```bash
# With auto-reload
python run.py

# Or directly with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Test API Endpoints
```bash
# Check if server is running
curl http://localhost:8000/

# Get portfolio summary
curl http://localhost:8000/api/v1/portfolio/summary

# Update prices
curl -X POST http://localhost:8000/api/v1/portfolio/update-prices
```

### 3. Database Operations
```bash
# Reinitialize database with fresh sample data
python scripts/init_data.py

# Access database directly (PostgreSQL)
postgresql3 data/portfolioPostgreSQL
.tables
.schema accounts
.schema assets
```

### 4. Add New Data
```bash
# Example: Add new account via API
curl -X POST http://localhost:8000/api/v1/accounts/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Fidelity", "account_type": "retirement"}'

# Example: Add new asset via API
curl -X POST http://localhost:8000/api/v1/assets/ \
  -H "Content-Type: application/json" \
  -d '{"account_id": 1, "symbol": "AMZN", "shares": 10, "avg_cost": 120.50}'
```

## 🧠 AI Analysis Features

### Portfolio Analysis
- **Diversity Score**: Based on number of assets and accounts
- **Risk Assessment**: Portfolio risk calculation
- **Recommendations**: HOLD, DIVERSIFY, or ACCUMULATE
- **Confidence Levels**: AI prediction confidence

### Sentiment Analysis (Optional)
- Requires `NEWS_API_KEY` environment variable
- Analyzes recent news for stock sentiment
- Returns bullish, bearish, or neutral sentiment

### Example AI Response
```json
{
  "total_value": 139230.45,
  "diversity_score": 0.7,
  "risk_score": 3.2,
  "recommendation": "HOLD",
  "confidence": 0.8,
  "insights": [
    "Portfolio spans 4 accounts",
    "Total of 12 different assets",
    "Diversity score: 70%"
  ]
}
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Port 8000 Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --port 8001
```

#### 2. Database Issues
```bash
# Delete and recreate database
rm data/portfolioPostgreSQL
python scripts/init_data.py
```

#### 3. Virtual Environment Issues
```bash
# Deactivate and recreate virtual environment
deactivate
rm -rf venv/
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

#### 4. Module Import Errors
```bash
# Make sure you're in the correct directory
pwd  # Should end with 'flexpesa-ai'

# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 5. Market Data Issues
```bash
# Test yfinance directly
python -c "import yfinance as yf; print(yf.Ticker('AAPL').info['regularMarketPrice'])"

# Check internet connection
ping finance.yahoo.com
```

### Debug Mode

Enable debug logging by modifying `run.py`:

```python
import uvicorn
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )
```

## 🧪 Testing

### Manual Testing
```bash
# Test all endpoints
curl http://localhost:8000/api/v1/portfolio/summary
curl -X POST http://localhost:8000/api/v1/portfolio/update-prices
curl http://localhost:8000/api/v1/accounts/
```

### Adding Test Framework (Optional)
```bash
# Install pytest
pip install pytest pytest-asyncio httpx

# Create test file (tests/test_api.py)
# Run tests
pytest
```

## 🚀 Production Deployment

### Environment Setup
```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Deployment (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production
```env
DATABASE_URL=postgresql://user:password@localhost/portfolio_db
NEWS_API_KEY=your_production_news_api_key
ENVIRONMENT=production
```

## 📞 API Support

### Health Check
- **Endpoint**: `GET /`
- **Response**: API status and available endpoints

### Error Responses
All endpoints return standardized error responses:

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

### CORS Configuration
The API is configured to accept requests from any origin for development. Update CORS settings in `app/main.py` for production.

## 🔗 Integration

### Frontend Integration
The API is designed to work with the Next.js frontend in `../flexpesa-client/`. Make sure both services are running:

- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000

### External APIs Used
- **Yahoo Finance (yfinance)**: Real-time stock prices
- **NewsAPI (optional)**: Sentiment analysis data

## 📝 License

This project is for educational and demonstration purposes. Make sure to comply with data provider terms of service when using in production.

---

**Need Help?** 
- Check the interactive API docs at http://localhost:8000/docs
- Review the troubleshooting section above
- Ensure the virtual environment is activated and dependencies are installed