# 🚀 Simple Setup - No Database Required!

## What You Actually Need

**Minimum Requirements:**
- ✅ **Python 3.10+** (that's it!)
- ❌ **No Database needed** (signals generated on demand)
- ❌ **No Docker needed** (run directly)

## Why Each Component Exists

### Database
- **Purpose**: Stores signals so they persist and can be listed
- **When needed**: If you want to see a list of all past signals
- **Alternative**: Generate signals on-demand (simpler, no persistence)

### Docker
- **Purpose**: Convenience to run everything in containers
- **When needed**: Only if you want isolated environments
- **Alternative**: Run Python directly (simpler, faster)

### ML Service
- **Purpose**: Generates AI trading signals
- **Required**: ✅ Yes - this is the core functionality

## Simplest Way to Run (No Database)

### Step 1: Install Python Dependencies
```bash
cd /Users/developer/ai-sentiment-market-prediction
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Start ML Service
```bash
# Terminal 1
source venv/bin/activate
uvicorn ml_service.main:app --port 8000
```

### Step 3: Start Simple Homepage (No Database)
```bash
# Terminal 2
source venv/bin/activate
streamlit run dashboard/homepage_simple.py --server.port 8501
```

**That's it!** Open http://localhost:8501

## What's the Difference?

### With Database (Current Setup)
- ✅ Shows list of all past signals
- ✅ Signals persist across restarts
- ❌ Requires PostgreSQL setup
- ❌ More complex

### Without Database (Simple Setup)
- ✅ No database setup needed
- ✅ Generate signals on-demand
- ✅ Simpler to run
- ❌ No list of past signals
- ❌ Signals don't persist

## Recommendation

**For development/testing**: Use the simple setup (no database)
**For production**: Use database setup (for signal history)

## Quick Start - Simple Version

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start ML service (Terminal 1)
uvicorn ml_service.main:app --port 8000

# 3. Start simple homepage (Terminal 2)  
streamlit run dashboard/homepage_simple.py --server.port 8501
```

Open http://localhost:8501 and generate signals!

