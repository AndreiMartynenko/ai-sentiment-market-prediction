# Running the ProofOfSignal Homepage

## Quick Start

### Option 1: Run Homepage Directly

```bash
# Make sure you're in the project root
cd /Users/developer/ai-sentiment-market-prediction

# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run the homepage
streamlit run dashboard/homepage.py --server.port 8501
```

### Option 2: Run with Docker

Update your `docker-compose.yml` to use `homepage.py` instead of `crypto_dashboard.py`:

```yaml
dashboard:
  ...
  command: streamlit run dashboard/homepage.py --server.port 8501
```

Then:
```bash
docker-compose up -d dashboard
```

## Database Migration

If you have an existing database, run the migration to add the `tx_signature` field:

```bash
# Connect to your PostgreSQL database
psql -h localhost -U postgres -d sentiment_market

# Run the migration
\i database/migration_add_tx_signature.sql
```

Or run it directly:
```bash
psql -h localhost -U postgres -d sentiment_market -f database/migration_add_tx_signature.sql
```

## Features

The homepage displays:

1. **Header Navigation**: ProofOfSignal logo with Home, About, Prices, Contact Us, Log In, Sign Up
2. **Signal List**: 
   - Crypto logo (emoji)
   - Timestamp
   - Signal type (BUY/SELL/HOLD) with color coding
   - Accuracy (confidence percentage)
   - Solana blockchain link (if published)

## API Endpoints

The homepage uses:
- `GET /signals/list` - Fetches list of all signals with Solana proof data

## Generating Signals

To generate signals that will appear on the homepage:

1. Use the ML service API:
   ```bash
   curl -X POST http://localhost:8000/hybrid \
     -H "Content-Type: application/json" \
     -d '{"symbol": "BTCUSDT"}'
   ```

2. The signal will automatically be published to Solana testnet and saved with transaction signature

## Access

Once running, access the homepage at:
- http://localhost:8501

