# 🔐 ProofOfSignal - Simple Setup Guide

## What You Need

**Only Python 3.10+** - That's it! No database, no Docker.

## Quick Start

### Option 1: One Command
```bash
./start.sh
```

### Option 2: Manual (2 terminals)

**Terminal 1 - ML Service:**
```bash
source venv/bin/activate
uvicorn ml_service.main:app --reload --port 8000
```

**Terminal 2 - Homepage:**
```bash
source venv/bin/activate
streamlit run dashboard/homepage.py --server.port 8501
```

Then open: **http://localhost:8501**

## What This Version Does

✅ **Generates AI trading signals** - Uses sentiment + technical analysis
✅ **Publishes to Solana** - Blockchain verification (optional)
✅ **Simple interface** - Clean homepage with header navigation
✅ **No database** - Signals stored in memory (last 100)
✅ **No Docker** - Runs directly with Python

## Features

- 🔐 **ProofOfSignal** header with navigation
- 📊 Generate signals for any crypto symbol
- 📈 View BUY/SELL/HOLD signals with accuracy
- ⛓️ Solana blockchain links for verification
- 🎨 Beautiful, modern UI

## First Time Setup

```bash
# 1. Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Run
./start.sh
```

## How to Use

1. Open http://localhost:8501
2. Enter a crypto symbol (e.g., `BTCUSDT`, `ETHUSDT`)
3. Click "Generate Signal"
4. View the signal with blockchain verification

## Troubleshooting

**Port in use?**
```bash
lsof -i :8000  # ML Service
lsof -i :8501  # Dashboard
kill -9 <PID>
```

**Missing dependencies?**
```bash
pip install uvicorn streamlit fastapi requests transformers torch pandas-ta solana
```

**ML Service not starting?**
```bash
tail -f /tmp/ml_service.log
```

## What's Removed

❌ Docker files
❌ Database dependencies  
❌ PostgreSQL setup
❌ Complex configuration

## Files Used

- `ml_service/main.py` - ML service (no database)
- `dashboard/homepage.py` - Simple homepage
- `start.sh` - Startup script

---

**That's it! Super simple! 🚀**

