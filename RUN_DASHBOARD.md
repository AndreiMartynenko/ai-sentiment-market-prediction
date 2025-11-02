# 🚀 How to Run the Dashboard

## ✅ Quick Start (Fastest Method)

### Add Database Config to `.env`

You need to add database configuration to your `.env` file. Add these lines:

```bash
# Add to your .env file
DB_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=sentiment_market
POSTGRES_PORT=5432

DATABASE_URL=postgres://postgres:postgres@localhost:5432/sentiment_market?sslmode=disable
```

### Option 1: Using Docker (Recommended - Easiest)

```bash
# 1. Start all services with Docker
docker-compose up -d

# 2. Wait a moment for services to start
sleep 10

# 3. Access dashboard
open http://localhost:8501
```

**That's it!** Docker handles everything automatically.

---

### Option 2: Local Python Setup

#### Step 1: Setup PostgreSQL

```bash
# Option A: If you have Docker
docker run -d \
  --name sentiment_postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=sentiment_market \
  -p 5432:5432 \
  postgres:15-alpine

# Wait for it to start
sleep 5

# Initialize database
docker exec -i sentiment_postgres psql -U postgres < database/schema.sql
docker exec -i sentiment_postgres psql -U postgres < database/seed_data.sql

# Option B: If you have local PostgreSQL
# First, set the password or use your existing credentials
# Then run:
psql -U postgres -c "CREATE DATABASE sentiment_market;"
psql -U postgres -d sentiment_market -f database/schema.sql
psql -U postgres -d sentiment_market -f database/seed_data.sql
```

#### Step 2: Activate Virtual Environment & Install

```bash
# Activate venv
source venv/bin/activate

# Install dashboard dependencies (if not already installed)
pip install streamlit plotly psycopg2-binary pandas streamlit-autorefresh

# Or install all requirements
pip install -r requirements.txt
```

#### Step 3: Add DB Config to `.env`

**Important:** Add database configuration to your `.env` file:

```bash
# Add these lines to .env
DB_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=sentiment_market
POSTGRES_PORT=5432
```

#### Step 4: Run Dashboard

```bash
cd dashboard
streamlit run app.py
```

Open your browser: **http://localhost:8501**

---

## 🔍 Troubleshooting

### "Database connection error"

**Issue**: Can't connect to PostgreSQL

**Solutions**:
1. ✅ Make sure PostgreSQL is running:
   ```bash
   docker ps | grep postgres
   # OR
   pg_isready
   ```

2. ✅ Check `.env` has correct DB credentials:
   ```bash
   DB_HOST=localhost
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=sentiment_market
   ```

3. ✅ If using Docker, wait for DB to be ready:
   ```bash
   docker-compose logs postgres
   ```

### "No data available"

**Issue**: Dashboard loads but shows no data

**Solution**: Load seed data:
```bash
# If using Docker
docker exec -i sentiment_postgres psql -U postgres -d sentiment_market < database/seed_data.sql

# If using local PostgreSQL
psql -U postgres -d sentiment_market -f database/seed_data.sql
```

### PostgreSQL Password Issues

**Issue**: "fe_sendauth: no password supplied"

**Solutions**:

1. **Using Docker** (recommended - no password hassles):
   ```bash
   docker-compose up -d postgres
   ```

2. **Local PostgreSQL** - Configure password:

   Edit `~/.pgpass` or use connection string:
   ```bash
   # Try without password first (if peer auth is configured)
   psql -U postgres -d postgres
   
   # Or set environment variable
   export PGPASSWORD=postgres
   ```

3. **Create database manually**:
   ```bash
   # Connect without password if possible
   psql -U postgres
   
   # Then inside psql:
   CREATE DATABASE sentiment_market;
   \q
   
   # Now run schema
   psql -U postgres -d sentiment_market < database/schema.sql
   ```

### Import Errors

**Issue**: "ModuleNotFoundError" or import errors

**Solution**: Install requirements:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Streamlit Auto-refresh Error

**Issue**: Import error for `streamlit_autorefresh`

**Solution**: 
```bash
pip install streamlit-autorefresh
```

---

## 🎯 Verify Setup

### Check Database Has Data

```bash
# Using Docker
docker exec sentiment_postgres psql -U postgres -d sentiment_market -c "SELECT COUNT(*) FROM market_data;"

# Or locally (adjust password as needed)
psql -U postgres -d sentiment_market -c "SELECT COUNT(*) FROM market_data;"
```

Should return a count > 0.

### Check Dashboard is Running

```bash
# Check if dashboard is accessible
curl http://localhost:8501
```

---

## 📊 Dashboard Features to Try

Once running, explore:

1. **Symbol Selector**: Switch between BTC-USDT, ETH-USDT, SOL-USDT
2. **Time Ranges**: Try 1D, 1W, 1M, 3M filters
3. **Refresh Button**: Click to manually reload data
4. **5 Tabs**:
   - 📊 Market Overview: Candlestick charts
   - 🧠 AI Sentiment: Sentiment timeline
   - ⚙️ Technical Indicators: RSI & MACD
   - 🔗 Hybrid Signals: Trading signals
   - 🔒 Proof-of-Signal: Blockchain verification
5. **Auto-Refresh**: Dashboard updates every 60 seconds

---

## 🎉 Success!

If you see:
- ✅ Dashboard loads at http://localhost:8501
- ✅ Data displays in charts
- ✅ No connection errors
- ✅ Symbols can be switched

**You're all set!** 🚀

---

## Need Help?

Check these files:
- `dashboard/README.md` - Full dashboard documentation
- `dashboard/QUICKSTART.md` - Quick start guide
- `database/schema.sql` - Database structure
- `database/seed_data.sql` - Sample data

Or run:
```bash
# Check if all services are up
docker-compose ps

# View logs
docker-compose logs dashboard
docker-compose logs postgres
```

