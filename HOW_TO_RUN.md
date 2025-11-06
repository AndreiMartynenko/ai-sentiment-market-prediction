# 🚀 How to Run the ProofOfSignal App

This guide provides step-by-step instructions to run the ProofOfSignal application.

## 📋 Prerequisites

- **Docker & Docker Compose** (recommended) OR
- **Python 3.10+**, **PostgreSQL 15+**, **Go 1.21+** (for local development)

---

## 🐳 Method 1: Docker Compose (Recommended - Easiest)

### Step 1: Navigate to Project Directory
```bash
cd /Users/developer/ai-sentiment-market-prediction
```

### Step 2: Create Environment File (Optional)
```bash
# Copy example env file
cp env.example .env

# Edit if needed (API keys are optional)
nano .env
```

### Step 3: Start All Services
```bash
# Start all services (database, ML service, dashboard)
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### Step 4: Run Database Migration (if needed)
```bash
# If you have existing data, run migration to add tx_signature field
docker-compose exec postgres psql -U postgres -d sentiment_market -f /docker-entrypoint-initdb.d/../database/migration_add_tx_signature.sql
```

Or from your local machine:
```bash
psql -h localhost -U postgres -d sentiment_market -f database/migration_add_tx_signature.sql
```

### Step 5: Access the Application

- **🏠 Homepage**: http://localhost:8501
- **📚 ML Service API Docs**: http://localhost:8000/docs
- **🔍 API Health Check**: http://localhost:8000/health

### Stop Services
```bash
docker-compose down

# Stop and remove volumes (⚠️ deletes database data)
docker-compose down -v
```

---

## 💻 Method 2: Local Development

### Step 1: Start PostgreSQL Database

**Option A: Using Docker (Easiest)**
```bash
docker run -d \
  --name sentiment_postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=sentiment_market \
  -p 5432:5432 \
  postgres:15-alpine
```

**Option B: Local PostgreSQL**
Make sure PostgreSQL 15+ is installed and running locally.

### Step 2: Initialize Database
```bash
# Create database schema
psql -h localhost -U postgres -d sentiment_market -f database/schema.sql

# Run migration (adds tx_signature field)
psql -h localhost -U postgres -d sentiment_market -f database/migration_add_tx_signature.sql

# (Optional) Add seed data
psql -h localhost -U postgres -d sentiment_market -f database/seed_data.sql
```

### Step 3: Setup Python Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Start ML Service

**Terminal 1:**
```bash
# Make sure venv is activated
source venv/bin/activate

# Start ML service
uvicorn ml_service.main:app --reload --host 0.0.0.0 --port 8000
```

The ML service will be available at: http://localhost:8000

### Step 5: Start Homepage Dashboard

**Terminal 2:**
```bash
# Make sure venv is activated
source venv/bin/activate

# Start homepage
streamlit run dashboard/homepage.py --server.port 8501
```

The homepage will be available at: http://localhost:8501

---

## 🧪 Testing the Application

### 1. Check ML Service Health
```bash
curl http://localhost:8000/health
```

### 2. Generate a Signal
```bash
curl -X POST http://localhost:8000/hybrid \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT"}'
```

### 3. View Signals List
```bash
curl http://localhost:8000/signals/list
```

### 4. Open Homepage
Open your browser and navigate to: **http://localhost:8501**

You should see:
- ✅ Header with ProofOfSignal logo and navigation
- ✅ List of generated signals
- ✅ Each signal showing: logo, time, signal type, accuracy, Solana link

---

## 🔧 Troubleshooting

### Issue: Port Already in Use
```bash
# Find process using port
lsof -i :8000  # ML Service
lsof -i :8501  # Dashboard
lsof -i :5432  # PostgreSQL

# Kill process
kill -9 <PID>
```

### Issue: Database Connection Error
```bash
# Check PostgreSQL is running
docker ps | grep postgres
# or
pg_isready -h localhost -p 5432

# Test connection
psql -h localhost -U postgres -d sentiment_market
```

### Issue: No Signals Showing
```bash
# Check if signals exist in database
psql -h localhost -U postgres -d sentiment_market -c "SELECT COUNT(*) FROM hybrid_signals;"

# Generate a test signal
curl -X POST http://localhost:8000/hybrid \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT"}'
```

### Issue: Solana Wallet Not Found
The Solana integration will create a wallet file automatically on first use:
- File: `solana_wallet.json` (in project root)
- This is normal - the wallet will be created when first publishing to Solana

### Issue: Docker Build Failed
```bash
# Clean and rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

---

## 📊 Service URLs Summary

| Service | URL | Description |
|---------|-----|-------------|
| **Homepage** | http://localhost:8501 | Main dashboard with signals list |
| **ML Service** | http://localhost:8000 | FastAPI backend |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Health Check** | http://localhost:8000/health | Service health status |
| **PostgreSQL** | localhost:5432 | Database connection |

---

## 🎯 Quick Start Commands

### Docker (All-in-One)
```bash
# Start everything
docker-compose up -d

# View logs
docker-compose logs -f dashboard

# Stop everything
docker-compose down
```

### Local Development
```bash
# Terminal 1: ML Service
source venv/bin/activate
uvicorn ml_service.main:app --reload --port 8000

# Terminal 2: Dashboard
source venv/bin/activate
streamlit run dashboard/homepage.py --server.port 8501
```

---

## 📝 Next Steps

1. **Generate Signals**: Use the API or dashboard to generate trading signals
2. **View on Homepage**: Signals automatically appear on the homepage
3. **Check Solana**: Click "View on Solana Explorer" to see blockchain verification
4. **Explore API**: Visit http://localhost:8000/docs for full API documentation

---

## 🆘 Need Help?

- Check the logs: `docker-compose logs -f`
- Verify services: `docker-compose ps`
- Test API: `curl http://localhost:8000/health`
- Check database: `psql -h localhost -U postgres -d sentiment_market`

---

**🎉 You're all set! The ProofOfSignal app is now running!**

