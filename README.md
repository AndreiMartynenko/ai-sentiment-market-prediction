# 📈 AI-Driven Sentiment Market Prediction System

A comprehensive, production-ready system that combines **FinBERT sentiment analysis** with **technical indicators** to generate intelligent trading signals through a hybrid AI decision engine.

## 🎯 Project Overview

This system analyzes financial news sentiment using FinBERT, computes technical indicators (EMA, RSI, MACD), and combines both through a hybrid AI engine to generate actionable trading signals. All data is visualized in real-time through a Streamlit dashboard.

### Key Features

- ✅ **Sentiment Analysis**: FinBERT-powered financial text analysis
- ✅ **Technical Indicators**: EMA, RSI, MACD calculations using pandas-ta
- ✅ **Hybrid AI Engine**: Combines sentiment + technical analysis with configurable weights
- ✅ **RESTful API**: Go backend with Gin framework
- ✅ **ML Service**: FastAPI-based Python service for ML operations
- ✅ **Real-time Dashboard**: Streamlit interface with Plotly charts
- ✅ **PostgreSQL Database**: Robust data storage with optimized schemas
- ✅ **Docker Compose**: Full containerization for easy deployment

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Streamlit     │────▶│   Go API        │────▶│  PostgreSQL     │
│   Dashboard     │     │   (Port 8080)   │     │   Database      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                        │                        ▲
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │  Python ML      │
                         │  Service        │
                         │  (Port 8000)    │
                         └─────────────────┘
                                  │
                 ┌────────────────┼─────────────────┐
                 │                │                 │    │
                 ▼                ▼                 ▼
           FinBERT      Technical      Hybrid
         Sentiment      Indicators     Engine
         Analysis       (pandas-ta)
```

## 📂 Project Structure

```
ai_sentiment-market-prediction/
│
├── cmd/
│   └── main.go                      # Go API entry point
│
├── internal/
│   ├── api/                         # API routes and handlers
│   │   ├── routes.go
│   │   └── handlers.go
│   ├── db/                          # Database connection
│   │   └── db.go
│   ├── models/                      # Data models
│   │   └── models.go
│   └── config/                      # Configuration management
│       └── config.go
│
├── ml_service/                      # Python ML Service
│   ├── sentiment.py                 # FinBERT sentiment analysis
│   ├── indicators.py                # Technical indicators (EMA, RSI, MACD)
│   ├── hybrid_engine.py             # Hybrid decision engine
│   └── main.py                      # FastAPI application
│
├── dashboard/
│   └── app.py                       # Streamlit dashboard
│
├── database/
│   ├── schema.sql                   # PostgreSQL schema
│   └── seed_data.sql                # Sample data
│
├── tests/
│   ├── test_sentiment.py
│   ├── test_technical.py
│   └── test_hybrid.py
│
├── docker-compose.yml               # Docker orchestration
├── Dockerfile.api                   # Go API container
├── Dockerfile.ml                    # ML Service container
├── Dockerfile.dashboard             # Dashboard container
├── requirements.txt                 # Python dependencies
├── go.mod                           # Go dependencies
└── README.md                        # This file
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Go 1.21+ (for local development)
- Python 3.10+ (for local development)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai_sentiment-market-prediction
```

### 2. Environment Setup

Create a `.env` file in the project root:

```bash
# API Keys (Optional - for external data sources)
NEWS_API_KEY=your_news_api_key_here
BINANCE_API_KEY=your_binance_api_key_here

# Database Configuration (Optional - defaults used if not set)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=sentiment_market
```

### 3. Start with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 4. Access Services

- **Go API**: http://localhost:8080
- **ML Service**: http://localhost:8000
- **Dashboard**: http://localhost:8501
- **PostgreSQL**: localhost:5432

## 📡 API Documentation

### Health Check

```bash
curl http://localhost:8080/api/v1/health
```

### Get Trading Signals

```bash
# Get all signals
curl http://localhost:8080/api/v1/signals

# Get signals for specific symbol
curl http://localhost:8080/api/v1/signals/BTCUSDT
```

### Sentiment Analysis

```bash
# Analyze sentiment (via ML service)
curl -X POST http://localhost:8000/sentiment/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Bitcoin reaches new all-time high amid strong institutional demand"}'
```

### Technical Indicators

```bash
# Calculate technical indicators
curl -X POST http://localhost:8000/technical/calculate \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "period": "7d"}'
```

### Generate Hybrid Signal

```bash
# Generate hybrid trading signal
curl -X POST http://localhost:8000/hybrid/generate \
  -H "Content-Type: application/json" \
  -d '{
    "sentiment_score": 0.75,
    "technical_score": 0.80,
    "sentiment_confidence": 0.9,
    "technical_confidence": 0.85
  }'
```

## 🧪 Testing

### Run Python Tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_sentiment.py -v
```

### Test Sentiment Analysis

```bash
python ml_service/sentiment.py
```

### Test Technical Indicators

```bash
python ml_service/indicators.py
```

### Test Hybrid Engine

```bash
python ml_service/hybrid_engine.py
```

## 📊 Usage Examples

### Example 1: Analyze News Sentiment

```python
from ml_service.sentiment import get_analyzer

analyzer = get_analyzer()
text = "Apple reports record-breaking quarterly earnings"

result = analyzer.analyze(text)
print(f"Sentiment: {result['label']}")
print(f"Score: {result['score']}")
print(f"Confidence: {result['confidence']}")
```

### Example 2: Calculate Technical Indicators

```python
from ml_service.indicators import get_indicators
import pandas as pd
import yfinance as yf

# Fetch market data
ticker = yf.Ticker("BTC-USD")
df = ticker.history(period="30d")

# Calculate indicators
indicators = get_indicators()
result = indicators.analyze(df)

print(f"EMA 20: {result['ema20']}")
print(f"RSI: {result['rsi']}")
print(f"Technical Score: {result['technical_score']}")
```

### Example 3: Generate Trading Signal

```python
from ml_service.hybrid_engine import get_engine

engine = get_engine(sentiment_weight=0.4, technical_weight=0.6)

result = engine.generate_signal(
    sentiment_score=0.85,
    technical_score=0.75
)

print(f"Signal: {result['signal']}")
print(f"Hybrid Score: {result['hybrid_score']}")
print(f"Reason: {result['reason']}")
```

## 🗄️ Database Schema

### Tables

1. **news_raw**: Raw news articles
2. **market_data**: OHLCV market data
3. **sentiment_results**: FinBERT sentiment analysis
4. **technical_indicators**: EMA, RSI, MACD calculations
5. **hybrid_signals**: Final trading signals

### Views

- `latest_signals`: Most recent signal per symbol
- `sentiment_summary`: Aggregate sentiment by symbol
- `technical_summary`: Aggregate technical indicators
- `hybrid_summary`: Aggregate hybrid signals

### Query Example

```sql
-- Get latest signals with high confidence
SELECT * FROM latest_signals 
WHERE confidence > 0.75 
ORDER BY hybrid_score DESC;
```

## 🔧 Configuration

### Adjust Hybrid Engine Weights

```bash
# Configure weights dynamically
curl -X POST http://localhost:8000/engine/configure \
  -H "Content-Type: application/json" \
  -d '{"sentiment_weight": 0.5, "technical_weight": 0.5}'
```

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `ML_SERVICE_URL`: ML service endpoint
- `NEWS_API_KEY`: NewsAPI key for news collection
- `BINANCE_API_KEY`: Binance API key for market data

## 📈 Dashboard Features

The Streamlit dashboard provides:

- **Real-time Signals**: Live trading signals with confidence scores
- **Price Charts**: Interactive candlestick charts with signal markers
- **Sentiment Analysis**: Sentiment score trends over time
- **Technical Indicators**: RSI, MACD, and other indicators visualization
- **Historical Data**: View past signals and performance
- **Symbol Selection**: Switch between different trading symbols

## 🛠️ Development

### Local Development Setup

#### Go API

```bash
cd cmd
go run main.go
```

#### Python ML Service

```bash
pip install -r requirements.txt
uvicorn ml_service.main:app --reload
```

#### Streamlit Dashboard

```bash
streamlit run dashboard/app.py
```

### Code Quality

```bash
# Go formatting
go fmt ./...

# Go vet
go vet ./...

# Python formatting
black ml_service/ dashboard/ tests/
flake8 ml_service/ dashboard/ tests/
```

## 📋 TODO / Roadmap

- [ ] Implement real-time data collection from NewsAPI
- [ ] Add Binance/binance API integration for live market data
- [ ] Implement backtesting framework
- [ ] Add WebSocket support for real-time dashboard updates
- [ ] Implement signal notification system (Telegram/Email)
- [ ] Add portfolio management features
- [ ] Implement strategy performance tracking
- [ ] Add support for additional symbols
- [ ] Create automated trading integration (paper trading)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **FinBERT**: [ProsusAI/finbert](https://huggingface.co/ProsusAI/finbert)
- **Transformers**: [Hugging Face](https://huggingface.co/transformers/)
- **pandas-ta**: [pandas-ta](https://github.com/twopirllc/pandas-ta)
- **Streamlit**: [Streamlit](https://streamlit.io/)

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Check the documentation in `/docs`
- Review API docs at http://localhost:8000/docs (ML Service)

