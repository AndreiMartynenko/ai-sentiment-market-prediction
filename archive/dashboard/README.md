# 🧠 AI-Blockchain Hybrid Market Predictor Dashboard

## 📖 Overview

The AI-Blockchain Hybrid Market Predictor is a comprehensive Streamlit dashboard that visualizes sentiment, technical, and on-chain indicators for cryptocurrency trading. The dashboard integrates AI-driven analysis with blockchain-based Proof-of-Signal verification on Solana.

### Key Features

- 📊 **Real-time Market Data**: Live OHLCV candlestick charts with EMA overlays
- 🧠 **AI Sentiment Analysis**: FinBERT-powered sentiment scoring with confidence levels
- ⚙️ **Technical Indicators**: RSI, MACD, and EMA analysis
- 🔗 **Hybrid AI Signals**: Combined sentiment and technical analysis for trading signals
- 🔒 **Proof-of-Signal**: Blockchain verification system with Solana integration
- 🔄 **Auto-Refresh**: Automatic data updates every 60 seconds
- 📱 **Modern UI**: Beautiful, responsive design with Plotly interactive charts

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL database (running and accessible)
- Required Python packages (see `requirements.txt`)

### Installation

1. **Clone the repository** (if not already done):
```bash
cd ai-sentiment-market-prediction
```

2. **Create virtual environment** (if not using existing):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
Create a `.env` file in the project root:
```bash
# Database Configuration
DB_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=sentiment_market
POSTGRES_PORT=5432

# Optional: ML Service URL
ML_SERVICE_URL=http://localhost:8000
```

5. **Ensure PostgreSQL is running** with the required schema:
```bash
# Run the schema if needed
psql -U postgres -d sentiment_market -f database/schema.sql
```

### Running the Dashboard

```bash
cd dashboard
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

---

## 📊 Dashboard Sections

### 1️⃣ Sidebar Controls

- **📊 Symbol Selector**: Choose from BTC-USDT, ETH-USDT, or SOL-USDT
- **⏱️ Time Range Selector**: Filter data by 1D, 1W, 1M, or 3M
- **🔄 Refresh Button**: Manually reload data from database
- **📈 Signal Thresholds**: View BUY/HOLD/SELL thresholds
- **🔗 Database Status**: Connection indicator

### 2️⃣ Main KPIs (Top Row)

The dashboard displays four key metrics:
- **💰 Current Price**: Latest market price from `market_data`
- **📊 Last Signal**: Most recent trading signal (BUY/SELL/HOLD)
- **🎯 Confidence Level**: AI confidence percentage
- **📊 Sentiment Trend**: Current sentiment direction with emoji indicators

### 3️⃣ Tabs

#### 📊 Market Overview
- **Candlestick Chart**: OHLC price visualization with color coding
- **EMA Overlays**: EMA20 (orange) and EMA50 (blue) lines
- **Latest Data**: Expandable table with recent market data

#### 🧠 AI Sentiment
- **Sentiment Timeline**: Line chart of sentiment scores over time (-1.0 to +1.0)
- **Color Zones**: Green (positive) and red (negative) background bands
- **Statistics**: Average sentiment, positive/negative ratios
- **Recent Results**: Expandable table with latest sentiment analysis

#### ⚙️ Technical Indicators
- **RSI Chart**: Relative Strength Index with overbought (70) and oversold (30) levels
- **MACD Chart**: Moving Average Convergence Divergence indicator
- **Current Values**: Real-time display of EMA20, EMA50, RSI, and technical score
- **Recent Data**: Expandable table with latest technical indicators

#### 🔗 Hybrid Signals
- **Hybrid Score Timeline**: Score evolution with signal markers
- **Signal Markers**: 
  - 🟢 Triangle up for BUY signals
  - 🔴 Triangle down for SELL signals
  - ⚪ Circle for HOLD signals
- **Threshold Lines**: Visual indicators for BUY (>0.3) and SELL (<-0.3) levels
- **Recent Signals Table**: Last 15 signals with full details
- **Statistics**: Total signals, BUY/SELL/HOLD counts
- **Explainability Panel**: Detailed reasoning for current signal

#### 🔒 Proof-of-Signal
- **What is Proof-of-Signal?**: Explanation of blockchain verification
- **Recent Signals Table**: Signals with proof hashes
- **View Full Hash**: Select and view complete cryptographic hash
- **Solscan Link**: Clickable placeholder links to Solana explorer
- **Publish Button**: Publish latest signal to blockchain (placeholder)
- **Technical Implementation**: Detailed explanation of the system

---

## 🗄️ Database Schema

The dashboard connects to PostgreSQL and reads from these tables:

### `market_data`
- **Columns**: symbol, timestamp, open, high, low, close, volume
- **Purpose**: OHLCV price data for candlestick charts

### `sentiment_results`
- **Columns**: symbol, timestamp, sentiment_score, label, confidence
- **Purpose**: AI sentiment analysis results from FinBERT

### `technical_indicators`
- **Columns**: symbol, timestamp, ema20, ema50, rsi, macd, technical_score
- **Purpose**: Technical analysis calculations

### `hybrid_signals`
- **Columns**: symbol, timestamp, signal, hybrid_score, confidence, reason, **proof_hash**
- **Purpose**: Combined AI trading signals with blockchain proof

---

## 🔒 Proof-of-Signal System

### What is Proof-of-Signal?

Proof-of-Signal is an innovative blockchain-based verification system that publishes AI trading signals to the Solana blockchain. Each signal is cryptographically hashed and stored on-chain, creating an immutable, timestamped record.

### How It Works

1. **Hash Generation**: Signal data is hashed using SHA-256
2. **On-Chain Storage**: Hash is stored on Solana blockchain
3. **Verification**: Anyone can verify by:
   - Retrieving hash from blockchain
   - Recomputing hash from signal data
   - Comparing the two hashes

### Security Benefits

- ✅ **Tamper-Proof**: Cryptographic hashing ensures integrity
- ✅ **Public Verification**: Transparent, auditable records
- ✅ **Timestamped**: Proof of when prediction was made
- ✅ **Immutable**: Cannot be altered after writing

### Current Status

The current implementation is a **placeholder** that:
- Generates proof hashes using SHA-256
- Displays hashes with truncation for readability
- Provides placeholder Solscan links
- Prepares UI for full Solana integration

**Future enhancements** will include:
- Real Solana transaction integration
- IPFS storage for full metadata
- Smart contract verification
- Multi-signature wallets
- Gasless transactions

---

## ⚙️ Configuration

### Environment Variables

```bash
# Required
DB_HOST=localhost              # PostgreSQL host
POSTGRES_USER=postgres         # Database username
POSTGRES_PASSWORD=postgres     # Database password
POSTGRES_DB=sentiment_market   # Database name
POSTGRES_PORT=5432             # Database port

# Optional
ML_SERVICE_URL=http://localhost:8000  # ML service URL for future integration
```

### Caching

- **Database Connections**: Cached for 60 seconds
- **Query Results**: Cached for 60 seconds via `@st.cache_data(ttl=60)`
- **Auto-Refresh**: Dashboard updates every 60 seconds
- **Manual Refresh**: Click "🔄 Refresh Data" button to clear cache

---

## 📈 Signal Interpretation

### Hybrid Score Thresholds

| Signal | Hybrid Score Range | Interpretation |
|--------|-------------------|----------------|
| 🟢 **BUY** | > 0.3 | Strong bullish momentum detected |
| ⚪ **HOLD** | -0.3 to 0.3 | Neutral or mixed signals |
| 🔴 **SELL** | < -0.3 | Strong bearish momentum detected |

### Color Coding

- 🟢 **Green**: BUY signals, positive sentiment
- ⚪ **Gray**: HOLD signals, neutral sentiment
- 🔴 **Red**: SELL signals, negative sentiment

---

## 🐛 Troubleshooting

### No Data Available

**Symptom**: Dashboard shows "No data available" messages

**Solutions**:
1. ✅ Ensure PostgreSQL is running: `docker ps` or `systemctl status postgresql`
2. ✅ Check database connection settings in `.env`
3. ✅ Verify data exists for selected symbol
4. ✅ Run sentiment and technical analysis first
5. ✅ Check database logs for errors

### Connection Errors

**Symptom**: "Database connection error" message

**Solutions**:
1. ✅ Verify PostgreSQL credentials
2. ✅ Check network/firewall settings
3. ✅ Ensure database is created: `createdb sentiment_market`
4. ✅ Run schema: `psql -U postgres -d sentiment_market -f database/schema.sql`
5. ✅ Test connection: `psql -U postgres -d sentiment_market`

### Slow Performance

**Symptom**: Dashboard loads slowly or lags

**Solutions**:
1. ✅ Reduce data limit in queries (currently 200-500 rows)
2. ✅ Add more specific date filtering
3. ✅ Check database indexing on timestamp and symbol
4. ✅ Use PostgreSQL read replicas for production
5. ✅ Increase cache TTL values

### Symbols Not Showing

**Symptom**: Symbol selector has options but no data

**Solutions**:
1. ✅ Verify symbol format matches database (BTCUSDT vs BTC-USDT)
2. ✅ Check seed data was inserted
3. ✅ Verify time range includes data timestamps
4. ✅ Run: `SELECT DISTINCT symbol FROM market_data;`

---

## 🧪 Testing

### Manual Testing

1. **Start dashboard**: `streamlit run app.py`
2. **Test symbol switching**: Change symbol in sidebar
3. **Test time ranges**: Switch between 1D, 1W, 1M, 3M
4. **Test refresh**: Click refresh button and verify cache clear
5. **Test auto-refresh**: Wait 60 seconds and verify data updates
6. **Test tabs**: Navigate through all five tabs
7. **Test proof hash**: View and select different proof hashes

### Data Validation

```bash
# Check database connection
psql -U postgres -d sentiment_market -c "SELECT COUNT(*) FROM market_data;"

# Verify recent data
psql -U postgres -d sentiment_market -c "SELECT * FROM hybrid_signals ORDER BY timestamp DESC LIMIT 5;"

# Check symbols
psql -U postgres -d sentiment_market -c "SELECT DISTINCT symbol FROM market_data;"
```

---

## 🔮 Future Enhancements

### Short Term
- [ ] Real-time WebSocket updates
- [ ] Additional chart types (heatmaps, correlation matrices)
- [ ] Portfolio view for multiple symbols
- [ ] Export functionality (CSV, PDF)
- [ ] Custom alert thresholds

### Medium Term
- [ ] Historical backtesting visualization
- [ ] Performance metrics dashboard
- [ ] User authentication and preferences
- [ ] Dark mode theme
- [ ] Mobile-responsive optimizations

### Long Term
- [ ] Full Solana blockchain integration
- [ ] IPFS storage for signal metadata
- [ ] Smart contract deployment
- [ ] Multi-signature wallet support
- [ ] Decentralized oracle integration
- [ ] Cross-chain support (Ethereum, Polygon)

---

## 📚 Additional Resources

### Documentation
- **Main README**: `../README.md`
- **API Docs**: `../docs/API_DOCUMENTATION.md`
- **Architecture**: `../ARCHITECTURE.md`
- **Database Schema**: `../database/schema.sql`

### External Links
- **Streamlit Docs**: https://docs.streamlit.io/
- **Plotly Docs**: https://plotly.com/python/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Solana Docs**: https://docs.solana.com/

---

## 💡 Usage Tips

1. **Use auto-refresh**: Dashboard updates every 60s automatically
2. **Filter by time range**: Narrow down to focus on recent data
3. **Check explainability**: View reasoning for each signal
4. **Monitor confidence**: Higher confidence = more reliable signals
5. **Compare signals**: Use statistics to see signal distribution
6. **Proof-of-Signal**: Verify predictions on blockchain

---

## 🤝 Contributing

To contribute to the dashboard:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📄 License

See `../LICENSE` for license information

---

## 👥 Support

For issues or questions:
- 📧 Contact the development team
- 🐛 Open an issue on GitHub
- 📖 Check the main README
- 🔍 Review database schema

---

**Last Updated**: 2024
**Version**: 2.0.0
**Status**: ✅ Production Ready (with placeholder Solana integration)
