# 🚀 No Database Setup - Quick Start

## What This Is

A simplified version that runs **without**:
- ❌ PostgreSQL database
- ❌ Docker
- ✅ Just Python!

## How It Works

- **ML Service**: Generates signals on-demand, stores in memory (last 100 signals)
- **Homepage**: Simple interface to generate and view signals
- **Solana**: Still publishes signals to blockchain (optional)

## Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
cd /Users/developer/ai-sentiment-market-prediction
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Run Everything
```bash
./run_no_db.sh
```

**OR manually in 2 terminals:**

**Terminal 1:**
```bash
source venv/bin/activate
uvicorn ml_service.main_no_db:app --reload --port 8000
```

**Terminal 2:**
```bash
source venv/bin/activate
streamlit run dashboard/homepage_simple.py --server.port 8501
```

### Step 3: Open Browser
Open http://localhost:8501

## What You Can Do

1. **Generate Signals**: Enter a symbol (BTCUSDT, ETHUSDT, etc.) and click "Generate Signal"
2. **View Signals**: See the signal with BUY/SELL/HOLD, accuracy, and Solana link
3. **No Persistence**: Signals are stored in memory (lost when service restarts)

## Files Used

- `ml_service/main_no_db.py` - ML service without database
- `dashboard/homepage_simple.py` - Simple homepage interface
- `run_no_db.sh` - Startup script

## Differences from Full Version

| Feature | Full Version | No DB Version |
|---------|--------------|---------------|
| Database | ✅ PostgreSQL | ❌ In-memory only |
| Signal History | ✅ Persistent | ❌ Last 100 signals |
| Docker | ✅ Supported | ❌ Not needed |
| Setup Complexity | Medium | ⚡ Simple |

## Troubleshooting

**Port already in use?**
```bash
lsof -i :8000  # ML Service
lsof -i :8501  # Dashboard
kill -9 <PID>
```

**Missing dependencies?**
```bash
pip install uvicorn streamlit requests fastapi pydantic transformers torch pandas-ta solana
```

**ML Service not starting?**
```bash
tail -f /tmp/ml_service_no_db.log
```

## Next Steps

Once you're comfortable, you can:
1. Add database for persistence
2. Add Docker for deployment
3. Customize the homepage
4. Add more features

---

**That's it! Super simple setup! 🎉**

