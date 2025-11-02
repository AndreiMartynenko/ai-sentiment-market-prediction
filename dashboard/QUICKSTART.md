# 🚀 Quick Start Guide

## Running the Dashboard in 3 Steps

### Step 1: Install Dependencies

```bash
# If not already installed
pip install -r ../requirements.txt

# Or install specific dashboard dependencies
pip install streamlit plotly psycopg2-binary pandas streamlit-autorefresh
```

### Step 2: Set Up Environment

Create a `.env` file in the project root:

```bash
# .env file
DB_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=sentiment_market
POSTGRES_PORT=5432
```

### Step 3: Run the Dashboard

```bash
cd dashboard
streamlit run app.py
```

Open your browser to: **http://localhost:8501**

---

## Running with Docker

### Start Full Stack (Recommended)

```bash
# Start all services (PostgreSQL + API + ML + Dashboard)
docker-compose up -d

# Access dashboard at http://localhost:8501
```

### Start Only Dashboard (if DB already running)

```bash
# Ensure PostgreSQL is running
docker-compose up postgres -d

# Run dashboard locally
cd dashboard
streamlit run app.py
```

---

## First Time Setup

### Initialize Database

```bash
# Using docker-compose
docker-compose up postgres -d

# Or using psql directly
psql -U postgres -c "CREATE DATABASE sentiment_market;"
psql -U postgres -d sentiment_market -f database/schema.sql
psql -U postgres -d sentiment_market -f database/seed_data.sql
```

---

## Troubleshooting

### Dashboard Shows "No Data"

**Solution**: Make sure PostgreSQL has seed data:

```bash
# Check data exists
psql -U postgres -d sentiment_market -c "SELECT COUNT(*) FROM market_data;"

# If empty, load seed data
psql -U postgres -d sentiment_market -f database/seed_data.sql
```

### Connection Error

**Solution**: Check PostgreSQL is running:

```bash
# Check docker container
docker ps | grep postgres

# Or check local postgres
pg_isready

# Restart if needed
docker-compose restart postgres
```

### Import Errors

**Solution**: Reinstall requirements:

```bash
pip install --upgrade -r ../requirements.txt
```

---

## Next Steps

1. ✅ Dashboard is running
2. 📊 Try different symbols: BTC-USDT, ETH-USDT, SOL-USDT
3. ⏱️ Switch time ranges: 1D, 1W, 1M, 3M
4. 🔄 Click refresh button
5. 🔒 Explore Proof-of-Signal tab
6. 📈 View all 5 tabs with charts

---

## Support

Need help? Check:
- Full README: `dashboard/README.md`
- Database schema: `database/schema.sql`
- Main docs: `../README.md`

---

**That's it! You're ready to explore the AI-Blockchain Hybrid Market Predictor! 🎉**

