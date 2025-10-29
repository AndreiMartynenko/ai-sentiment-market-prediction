# 🚀 Quick Start Guide - AI-Driven Sentiment Market Prediction System

Complete guide to run the entire application.

## 📋 Prerequisites

- **Docker** and **Docker Compose** (recommended)
- OR **Python 3.10+**, **Go 1.21+**, **PostgreSQL 15+** (for local development)

---

## 🐳 Method 1: Docker Compose (Recommended)

### Step 1: Clone and Setup

```bash
# Navigate to project directory
cd ai_sentiment-market-prediction

# Create environment file
cp env.example .env

# Edit .env with your settings (optional)
nano .env
```

### Step 2: Start All Services

```bash
# Build and start all containers
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### Step 3: Access Services

- **Dashboard**: http://localhost:8501
- **Go API**: http://localhost:8080
- **ML Service**: http://localhost:8000
- **PostgreSQL**: localhost:5432

### Step 4: Verify Installation

```bash
# Health check - Go API
curl http://localhost:8080/api/v1/health

# Health check - ML Service
curl http://localhost:8000/health

# Health check - Dashboard
curl http://localhost:8501
```

### Step 5: Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## 💻 Method 2: Local Development

### Prerequisites Setup

#### 1. PostgreSQL

```bash
# Start PostgreSQL
docker run -d \
  --name sentiment_postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=sentiment_market \
  -p 5432:5432 \
  postgres:15-alpine

# Create tables
psql -h localhost -U postgres -d sentiment_market -f database/schema.sql

# (Optional) Add seed data
psql -h localhost -U postgres -d sentiment_market -f database/seed_data.sql
```

#### 2. Python Environment

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

#### 3. Go Environment

```bash
# Download dependencies
go mod download

# Verify Go installation
go version
```

### Start Services Individually

#### Terminal 1: ML Service (Python/FastAPI)

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start ML service
uvicorn ml_service.main:app --reload --host 0.0.0.0 --port 8000

# Service available at: http://localhost:8000
```

#### Terminal 2: Go API

```bash
# Navigate to cmd directory
cd cmd

# Run Go API
go run main.go

# Service available at: http://localhost:8080
```

#### Terminal 3: Streamlit Dashboard

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start dashboard
streamlit run dashboard/app.py

# Service available at: http://localhost:8501
```

---

## 🧪 Testing the Application

### 1. Test Sentiment Analysis

```bash
curl -X POST http://localhost:8000/sentiment \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "text": "Apple stock surges after strong earnings"}'
```

Or use Python:

```bash
python test_sentiment_api.py
```

### 2. Test Technical Indicators

```bash
curl -X POST http://localhost:8000/technical \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTC-USD"}'
```

Or use Python:

```bash
python test_technical_api.py
```

### 3. Test Hybrid Signals

```bash
curl -X POST http://localhost:8000/hybrid \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTC-USD"}'
```

Or use Python:

```bash
python test_hybrid_api.py
```

### 4. Access Dashboard

Open browser and navigate to:
```
http://localhost:8501
```

Select a symbol from the sidebar and explore:
- 📈 Market Overview
- 🧠 Sentiment Analysis
- ⚙️ Technical Indicators
- 🤖 Hybrid Signals

---

## 📊 Complete Workflow Example

### Step 1: Analyze Sentiment

```bash
# Analyze news sentiment
curl -X POST http://localhost:8000/sentiment \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC-USD",
    "text": "Bitcoin reaches new all-time high amid strong institutional adoption"
  }'
```

**Response:**
```json
{
  "symbol": "BTC-USD",
  "label": "positive",
  "sentiment_score": 0.82,
  "confidence": 0.91
}
```

### Step 2: Calculate Technical Indicators

```bash
# Get technical analysis
curl -X POST http://localhost:8000/technical \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTC-USD", "period": "3mo"}'
```

**Response:**
```json
{
  "symbol": "BTC-USD",
  "ema20": 95000.50,
  "ema50": 92000.25,
  "rsi": 64.5,
  "macd": 1250.75,
  "technical_score": 0.42
}
```

### Step 3: Generate Hybrid Signal

```bash
# Generate hybrid trading signal
curl -X POST http://localhost:8000/hybrid \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTC-USD"}'
```

**Response:**
```json
{
  "symbol": "BTC-USD",
  "sentiment_score": 0.74,
  "technical_score": 0.42,
  "hybrid_score": 0.62,
  "signal": "BUY",
  "confidence": 0.85,
  "reason": "Positive sentiment and bullish EMA/RSI"
}
```

### Step 4: View in Dashboard

1. Open http://localhost:8501
2. Select "BTC-USD" from sidebar
3. Navigate through tabs to see:
   - Price chart with signals
   - Sentiment timeline
   - Technical indicators
   - Hybrid signals with confidence

---

## 🔧 Troubleshooting

### Issue: Port Already in Use

```bash
# Find process using port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Issue: Database Connection Error

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Test connection
psql -h localhost -U postgres -d sentiment_market

# Check environment variables
echo $DB_HOST
echo $POSTGRES_USER
```

### Issue: Model Download Error (FinBERT)

```bash
# Manually download model
python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; AutoTokenizer.from_pretrained('yiyanghkust/finbert-tone'); AutoModelForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone')"

# Or set Hugging Face cache
export HF_HOME=/path/to/cache
```

### Issue: No Data in Dashboard

```bash
# Check if data exists in database
psql -h localhost -U postgres -d sentiment_market -c "SELECT COUNT(*) FROM hybrid_signals;"
psql -h localhost -U postgres -d sentiment_market -c "SELECT COUNT(*) FROM sentiment_results;"
psql -h localhost -U postgres -d sentiment_market -c "SELECT COUNT(*) FROM technical_indicators;"

# If empty, run analysis first
curl -X POST http://localhost:8000/sentiment -H "Content-Type: application/json" -d '{"symbol": "AAPL", "text": "Test"}'
```

### Issue: Docker Build Failed

```bash
# Clean and rebuild
docker-compose down -v
docker system prune -a
docker-compose build --no-cache
docker-compose up -d
```

---

## 📱 API Endpoints Summary

### Go API (Port 8080)

```
GET  /api/v1/health
GET  /api/v1/signals
GET  /api/v1/signals/:symbol
GET  /api/v1/sentiment
GET  /api/v1/sentiment/:symbol
GET  /api/v1/technical
GET  /api/v1/technical/:symbol
GET  /api/v1/news
GET  /api/v1/news/:symbol
GET  /api/v1/market
GET  /api/v1/market/:symbol
```

### ML Service (Port 8000)

```
GET  /health
POST /sentiment          # Analyze sentiment
POST /technical          # Calculate technical indicators
POST /hybrid             # Generate hybrid signals
GET  /models
GET  /models/{name}/info
POST /engine/configure   # Adjust hybrid weights
```

---

## 🔄 Development Workflow

1. **Start Infrastructure**:
   ```bash
   docker-compose up -d postgres
   ```

2. **Start Services**:
   ```bash
   # Terminal 1: ML Service
   uvicorn ml_service.main:app --reload

   # Terminal 2: Go API
   cd cmd && go run main.go

   # Terminal 3: Dashboard
   streamlit run dashboard/app.py
   ```

3. **Make Changes**:
   - Services auto-reload on file changes
   - Test via curl or test scripts
   - View results in dashboard

4. **Debug**:
   ```bash
   # View logs
   docker-compose logs -f ml-service
   docker-compose logs -f api

   # Check database
   docker-compose exec postgres psql -U postgres -d sentiment_market
   ```

---

## ✅ Verification Checklist

- [ ] Docker/PostgreSQL running
- [ ] Services accessible (API, ML Service, Dashboard)
- [ ] Database schema created
- [ ] Test API endpoints responding
- [ ] Dashboard loading without errors
- [ ] Can see data/charts for at least one symbol

---

## 📚 Additional Resources

- **README.md**: Project overview
- **ARCHITECTURE.md**: System architecture
- **docs/API_DOCUMENTATION.md**: Complete API documentation
- **dashboard/README.md**: Dashboard-specific docs
- **ml_service/README.md**: ML service documentation

---

## 🎯 Quick Command Reference

```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# View logs
docker-compose logs -f

# Restart service
docker-compose restart ml-service

# Access database
docker-compose exec postgres psql -U postgres -d sentiment_market

# Run tests
pytest tests/
python test_sentiment_api.py
python test_technical_api.py
python test_hybrid_api.py

# Clean everything
docker-compose down -v
docker system prune -a
```

---

**🎉 You're all set! Start analyzing and generating trading signals!**

