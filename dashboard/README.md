# Streamlit Dashboard Documentation

## Overview

The Streamlit dashboard provides a comprehensive, real-time visualization interface for the AI-Driven Sentiment Market Prediction System. It connects directly to PostgreSQL to display sentiment analysis, technical indicators, and hybrid trading signals.

## Features

### 📊 KPI Cards
- **Current Price**: Latest market price
- **Last Signal**: Most recent trading signal (BUY/SELL/HOLD)
- **Confidence**: Signal confidence percentage
- **Sentiment Trend**: Current sentiment direction

### 📈 Market Overview Tab
- **Candlestick Chart**: OHLC price visualization
- **EMA Overlays**: EMA20 (orange) and EMA50 (blue) lines
- **Latest Market Data**: Expandable data table

### 🧠 Sentiment Tab
- **Timeline Chart**: Sentiment scores over time (-1.0 to +1.0)
- **Color Coding**: Green for positive, red for negative, gray for neutral
- **Statistics**: Average sentiment, positive/negative ratios

### ⚙️ Technicals Tab
- **RSI Chart**: Relative Strength Index with overbought/oversold levels
- **MACD Chart**: Moving Average Convergence Divergence
- **Current Values**: Display of EMA20, EMA50, RSI, and technical score

### 🤖 Hybrid Signals Tab
- **Hybrid Score Timeline**: Score evolution over time
- **Signal Markers**: 
  - 🟢 Triangle up for BUY signals
  - 🔴 Triangle down for SELL signals
  - ⚪ Circle for HOLD signals
- **Confidence Bar Chart**: Visual confidence levels
- **Signals Table**: Last 10 signals with full details
- **Statistics**: Total signals, BUY/SELL counts

## Running the Dashboard

### Local Development

```bash
# Install dependencies
pip install streamlit plotly psycopg2-binary pandas

# Run the dashboard
streamlit run dashboard/app.py

# Access at http://localhost:8501
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# Access dashboard at http://localhost:8501
```

## Configuration

### Environment Variables

```bash
# Database Configuration
DB_HOST=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=sentiment_market
POSTGRES_PORT=5432
```

### Sidebar Controls

- **Symbol Selector**: Choose from available trading symbols
- **Time Range**: Filter data by time period
- **Refresh Button**: Manually reload data from database

## Data Flow

```
PostgreSQL Database
    ↓
Dashboard queries tables:
    - hybrid_signals
    - sentiment_results
    - technical_indicators
    - market_data
    ↓
Plotly visualizations
    ↓
Streamlit display
```

## Database Schema

The dashboard reads from these PostgreSQL tables:

### hybrid_signals
- timestamp, symbol, signal, hybrid_score, confidence, reason
- sentiment_score, technical_score

### sentiment_results
- timestamp, symbol, sentiment_score, label, confidence

### technical_indicators
- timestamp, symbol, ema20, ema50, rsi, macd, technical_score

### market_data
- timestamp, symbol, open, high, low, close, volume

## Signal Interpretation

### Hybrid Score Thresholds

- **BUY** (hybrid_score > 0.3): Strong bullish momentum
- **HOLD** (-0.3 ≤ hybrid_score ≤ 0.3): Neutral or mixed signals
- **SELL** (hybrid_score < -0.3): Strong bearish momentum

### Colors

- 🟢 **Green**: BUY signals, positive sentiment
- ⚪ **Gray**: HOLD signals, neutral sentiment
- 🔴 **Red**: SELL signals, negative sentiment

## Caching

The dashboard uses Streamlit's caching mechanism:
- **Database queries**: Cached for 60 seconds
- **Refresh button**: Clears cache and reloads data

## Troubleshooting

### No Data Available

If you see "No data available" messages:
1. Ensure PostgreSQL is running
2. Check database connection settings
3. Verify data exists for the selected symbol
4. Run sentiment and technical analysis first

### Connection Errors

If database connection fails:
1. Check PostgreSQL is accessible
2. Verify credentials in environment variables
3. Review Docker networking configuration
4. Check firewall settings

### Slow Loading

If the dashboard is slow:
1. Reduce data limit in queries
2. Add more specific date filtering
3. Check database indexing
4. Consider using read replicas

## Performance Optimization

- **Limit queries**: Default 100-200 rows per query
- **Caching**: 60-second cache on database connections
- **Indexed fields**: Ensure timestamp and symbol are indexed
- **Cleanup**: Run periodic data cleanup for old records

## Future Enhancements

- [ ] Real-time WebSocket updates
- [ ] Additional chart types (heatmaps, correlation)
- [ ] Portfolio view for multiple symbols
- [ ] Export functionality (CSV, PDF)
- [ ] Custom alert thresholds
- [ ] Historical backtesting visualization

## Support

For issues or questions:
- Check the main README.md
- Review database schema.sql
- Contact the development team

