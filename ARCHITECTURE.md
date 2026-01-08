# System Architecture Documentation

## Overview

The AI-Driven Sentiment Market Prediction System is a microservices-based application that analyzes financial market sentiment and technical indicators to generate intelligent trading signals.

Check the test file `test_api_endpoints.py` for API endpoint details.

## Architecture Components

### 1. Go API Backend (`internal/api/`)

**Technology**: Go 1.21, Gin Framework

**Responsibilities**:
- RESTful API endpoints for data retrieval
- Request/response handling
- Database query management
- External service integration

**Key Files**:
- `routes.go`: Route definitions
- `handlers.go`: HTTP handlers
- `config.go`: Configuration management
- `db.go`: Database connection pool

**Endpoints**:
- `GET /api/v1/health` - Health check
- `GET /api/v1/signals` - Retrieve trading signals
- `GET /api/v1/sentiment` - Retrieve sentiment analysis
- `GET /api/v1/technical` - Retrieve technical indicators
- `GET /api/v1/news` - Retrieve news articles
- `GET /api/v1/market` - Retrieve market data

### 2. Python ML Service (`ml_service/`)

**Technology**: Python 3.10, FastAPI, PyTorch

**Responsibilities**:
- Sentiment analysis using FinBERT
- Technical indicator calculations
- Hybrid decision engine
- Model inference

**Key Modules**:

#### 2.1 Sentiment Analysis (`sentiment.py`)
- **Model**: FinBERT (ProsusAI/finbert)
- **Input**: Financial text
- **Output**: Sentiment label (POSITIVE/NEGATIVE/NEUTRAL), score (0-1), confidence
- **Features**: 
  - Single and batch analysis
  - Confidence scoring
  - Normalized sentiment scores

#### 2.2 Technical Indicators (`indicators.py`)
- **Libraries**: pandas-ta, pandas, numpy
- **Indicators**: EMA (20, 50), RSI (14), MACD (12, 26, 9)
- **Input**: OHLCV data (DataFrame)
- **Output**: Technical score (0-1)
- **Features**:
  - Composite technical scoring
  - Signal strength calculation
  - Trend detection

#### 2.3 Hybrid Decision Engine (`hybrid_engine.py`)
- **Purpose**: Combine sentiment and technical analysis
- **Algorithm**: Weighted scoring with confidence adjustment
- **Input**: Sentiment score + Technical score
- **Output**: BUY/SELL/HOLD signal with reasoning
- **Features**:
  - Configurable weights
  - Confidence-based weighting
  - Human-readable reasoning

### 3. Streamlit Dashboard (`dashboard/`)

**Technology**: Streamlit, Plotly, Requests

**Responsibilities**:
- Real-time data visualization
- Interactive charts
- Signal display
- Historical analysis

**Features**:
- Price charts with candlesticks
- Sentiment trends
- Technical indicator overlays
- Signal markers
- Auto-refresh capability

### 4. PostgreSQL Database (`database/`)

**Technology**: PostgreSQL 15

**Schema**:

#### Tables:
1. **news_raw**: Raw news articles
2. **market_data**: OHLCV data
3. **sentiment_results**: FinBERT predictions
4. **technical_indicators**: Calculated indicators
5. **hybrid_signals**: Final trading signals

#### Views:
- `latest_signals`: Latest signal per symbol
- `sentiment_summary`: Aggregated sentiment
- `technical_summary`: Aggregated technicals
- `hybrid_summary`: Aggregated signals

#### Functions:
- `clean_old_data(days)`: Automated data cleanup

### 5. Docker Configuration

**Services**:
- `postgres`: Database container
- `api`: Go API container
- `ml-service`: Python ML container
- `dashboard`: Streamlit container

**Networking**: Bridge network with service discovery

**Volumes**: Persistent data storage

## Data Flow

### Signal Generation Flow

```
1. News Collection
   ├─> NewsAPI / RSS
   └─> Database (news_raw)

2. Market Data Collection
   ├─> yfinance / Binance
   └─> Database (market_data)

3. Sentiment Analysis
   ├─> Read news_raw
   ├─> FinBERT Processing
   └─> Database (sentiment_results)

4. Technical Analysis
   ├─> Read market_data
   ├─> pandas-ta Calculations
   └─> Database (technical_indicators)

5. Hybrid Decision
   ├─> Read sentiment_results
   ├─> Read technical_indicators
   ├─> Weighted Combination
   └─> Database (hybrid_signals)

6. Visualization
   ├─> Dashboard Requests
   ├─> API Retrieval
   └─> Real-time Display
```

## Deployment Architecture

### Development
```
Local Machine
├─> Go API (localhost:8080)
├─> Python ML (localhost:8000)
├─> Streamlit (localhost:8501)
└─> PostgreSQL (localhost:5432)
```

### Production (Docker)
```
Docker Network (sentiment_network)
├─> postgres:5432
├─> api:8080 (exposed)
├─> ml-service:8000 (internal)
└─> dashboard:8501 (exposed)
```

## Performance Considerations

### Caching Strategy
- PostgreSQL query caching
- In-memory model caching (FinBERT)
- Connection pooling

### Scalability
- Horizontal scaling via Docker
- Load balancing with Nginx (future)
- Database read replicas (future)

### Optimization
- Batch processing for sentiment
- Async API calls
- Efficient DataFrame operations

## Security

### API Security
- Input validation
- SQL injection prevention
- Rate limiting (future)

### Data Security
- Environment variables for secrets
- Database encryption
- HTTPS enforcement (future)

## Monitoring

### Logging
- Structured logging (JSON)
- Log rotation
- Centralized log aggregation (future)

### Metrics
- API response times
- Model inference latency
- Database query performance
- Signal accuracy tracking

## Error Handling

### Graceful Degradation
- Fallback to neutral signals on errors
- Retry mechanisms
- Circuit breakers

### Error Types
- External API failures
- Model loading errors
- Database connection issues
- Invalid input data

## Future Enhancements

1. **Real-time Processing**: WebSocket support for live updates
2. **Additional Models**: RoBERTa, DistilBERT support
3. **Backtesting Framework**: Historical performance analysis
4. **Trading Integration**: Paper trading and live execution
5. **Portfolio Management**: Multi-asset tracking
6. **Notification System**: Telegram/Email alerts
7. **Mobile App**: Native iOS/Android clients

