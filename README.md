# Investment Portfolio MVP - Startup Scripts

This directory contains scripts to easily run both the FastAPI backend and Next.js frontend together.

## 🚀 Quick Start

Choose the script that matches your operating system:

### Linux/Mac/Unix
```bash
chmod +x run.sh
./run.sh
```

### Windows
```batch
run.bat
```

### Cross-Platform (Python)
```bash
python run.py
# or
python3 run.py
```

## 📋 What the Scripts Do

1. **Check Prerequisites** - Verify Python 3.8+, Node.js 18+, and npm are installed
2. **Setup Backend** - Create virtual environment, install Python dependencies, initialize database
3. **Setup Frontend** - Install Node.js dependencies
4. **Start Services** - Run both FastAPI (port 8000) and Next.js (port 3000) concurrently
5. **Open Browser** - Automatically open http://localhost:3000

## 🛠️ Prerequisites

Make sure you have installed:

- **Python 3.8+** - [Download here](https://python.org/downloads/)
- **Node.js 18+** - [Download here](https://nodejs.org/)
- **npm** (comes with Node.js)

## 📱 Service URLs

Once running, you can access:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/redoc

## 🗂️ Project Structure

```
investment-portfolio/
├── run.sh                    # Unix/Linux/Mac startup script
├── run.bat                   # Windows startup script  
├── run.py                    # Cross-platform Python script
├── flexpesa-ai/              # FastAPI backend
│   ├── app/
│   ├── run.py
│   ├── requirements.txt
│   └── scripts/init_data.py
└── flexpesa-client/          # Next.js frontend
    ├── src/
    ├── package.json
    └── next.config.ts
```

## 🔧 Script Details

### run.sh (Unix/Linux/Mac)
- Creates Python virtual environment in `flexpesa-ai/venv/`
- Installs backend dependencies automatically
- Installs frontend dependencies automatically
- Runs both services concurrently with log output
- Handles graceful shutdown with Ctrl+C

### run.bat (Windows)
- Creates Python virtual environment in `flexpesa-ai\venv\`
- Installs all dependencies automatically
- Opens separate command windows for backend and frontend
- Services continue running independently

### run.py (Cross-Platform)
- Works on any OS with Python 3.8+
- Colored terminal output for better visibility
- Handles process management and cleanup
- Real-time log streaming from both services

## 📊 Sample Data

The scripts automatically initialize the database with sample data including:

- **Wells Fargo Intuitive** (AAPL, MSFT, SPY)
- **Stack Well** (QQQ, VTI, NVDA)
- **Cash App Investing** (TSLA, AMD, GOOGL)
- **Robinhood** (BTC-USD, ETH-USD)

Total portfolio value: ~$139,230

## 🐛 Troubleshooting

### Port Already in Use
If you get "port already in use" errors:
```bash
# Kill processes on port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Kill processes on port 3000 (frontend)  
lsof -ti:3000 | xargs kill -9
```

### Python Virtual Environment Issues
Delete the virtual environment and restart:
```bash
rm -rf flexpesa-ai/venv/
./run.sh
```

### Node.js Dependencies Issues
Clear npm cache and reinstall:
```bash
cd flexpesa-client/
rm -rf node_modules package-lock.json
npm install
```

### Permission Denied (Unix/Linux/Mac)
Make the script executable:
```bash
chmod +x run.sh
```

## 🔄 Manual Development

If you prefer to run services manually:

### Backend Only
```bash
cd flexpesa-ai/
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate.bat` on Windows
pip install -r requirements.txt
python scripts/init_data.py
python run.py
```

### Frontend Only
```bash
cd flexpesa-client/
npm install
npm run dev
```

## 🎯 Features

✅ **Real-time Portfolio Tracking** - Live market data via yfinance  
✅ **Multi-Account Support** - Wells Fargo, Stack Well, Cash App, Robinhood  
✅ **AI Analysis** - Portfolio insights and recommendations  
✅ **Responsive Design** - Works on desktop, tablet, and mobile  
✅ **Asset Management** - Add/track individual holdings  
✅ **Live Price Updates** - Real-time market data  

## 🚀 Production Deployment

For production deployment, see:
- [Backend Deployment Guide](flexpesa-ai/README.md)
- [Frontend Deployment Guide](flexpesa-client/README.md)

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Check log files for detailed error messages
4. Ensure no other services are using ports 3000 or 8000