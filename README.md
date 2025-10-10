# 🚀 AI Sentiment Market Prediction System

A comprehensive, research-grade AI system for sentiment analysis and market prediction using advanced machine learning techniques. This system is designed for academic research and dissertation purposes, providing a complete pipeline from data collection to trading signal generation.

## 🎯 Overview

This system combines state-of-the-art natural language processing with financial market analysis to predict market movements based on sentiment extracted from news articles, social media, and other textual sources. The system is built with scalability, reliability, and academic rigor in mind.

## 🏗️ Architecture

### System Components

- **🔧 Go Backend API**: High-performance REST API for signal processing and data management
- **🤖 Python ML Service**: Advanced sentiment analysis using multiple transformer models
- **📊 Data Pipeline**: Comprehensive data collection from multiple sources
- **🗄️ PostgreSQL Database**: Robust data storage with optimized schemas
- **📱 Telegram Bot**: Real-time notifications and alerts
- **📈 Monitoring**: Prometheus and Grafana for system monitoring

### Tech Stack

- **Backend**: Go 1.21, Gin framework, PostgreSQL
- **ML/AI**: Python 3.10, PyTorch, Transformers, FinBERT, RoBERTa
- **Data**: yfinance, NewsAPI, Twitter API, Reddit API
- **Infrastructure**: Docker, Docker Compose, Nginx, Redis
- **Monitoring**: Prometheus, Grafana
- **Testing**: pytest, Go testing framework

## 📁 Project Structure

```
ai-sentiment-market-prediction/
│
├── 📄 README.md                    # This file
├── 📄 requirements.txt            # Python dependencies
├── 📄 go.mod                      # Go dependencies
├── 📄 docker-compose.yml          # Docker orchestration
├── 📄 env.example                # Environment configuration
│
├── 📁 backend/                    # Go backend API
│   └── main.go                   # Main application entry point
│
├── 📁 golang-api/                 # Go API structure
│   ├── internal/
│   │   ├── handlers/             # HTTP handlers
│   │   ├── services/             # Business logic
│   │   └── models/               # Data models
│   └── config/                   # Configuration
│
├── 📁 src/                        # Python source code
│   ├── ml_service.py             # ML service (FastAPI)
│   ├── enhanced_data_pipeline.py # Data collection & preprocessing
│   ├── sentiment_analysis.py    # Sentiment analysis scripts
│   ├── signal_generator.py      # Trading signal generation
│   └── telegram_bot.py          # Telegram bot implementation
│
├── 📁 database/                   # Database schemas and migrations
│   └── schema.sql                # PostgreSQL schema
│
├── 📁 docker/                     # Docker configuration
│   ├── Dockerfile.go            # Go backend container
│   ├── Dockerfile.python        # Python ML service container
│   └── nginx.conf               # Nginx configuration
│
├── 📁 docs/                       # Documentation
│   └── API_DOCUMENTATION.md     # Comprehensive API docs
│
├── 📁 tests/                      # Test suites
│   └── test_comprehensive.py    # Comprehensive test suite
│
├── 📁 data/                       # Data storage
│   ├── raw/                     # Raw collected data
│   └── processed/               # Processed and cleaned data
│
├── 📁 models/                     # ML model storage
├── 📁 logs/                       # Application logs
└── 📁 reports/                    # Analysis reports and results
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.10+ (for local development)
- Go 1.21+ (for local development)
- PostgreSQL 15+ (if running locally)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ai-sentiment-market-prediction.git
cd ai-sentiment-market-prediction
```

### 2. Environment Setup

```bash
# Copy environment template
cp env.example .env

# Edit .env with your API keys and configuration
nano .env
```

### 3. Start with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Verify Installation

```bash
# Check Go API health
curl http://localhost:8080/api/v1/health

# Check ML service health
curl http://localhost:8000/health

# Check database connection
docker-compose exec postgres psql -U postgres -d sentiment_prediction -c "SELECT version();"
```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# API Keys (Required for full functionality)
NEWS_API_KEY=your_news_api_key_here
TWITTER_API_KEY=your_twitter_api_key_here
TELEGRAM_TOKEN=your_telegram_bot_token_here

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_NAME=sentiment_prediction

# ML Configuration
MODEL_PATH=./models
BATCH_SIZE=32
CONFIDENCE_THRESHOLD=0.7

# Trading Configuration
DEFAULT_SYMBOLS=AAPL,GOOGL,MSFT,TSLA,AMZN,NVDA,META,NFLX
SIGNAL_STRENGTH_THRESHOLD=0.6
```

### API Keys Setup

1. **NewsAPI**: Get free API key from [NewsAPI.org](https://newsapi.org/)
2. **Twitter API**: Apply for developer access at [Twitter Developer Portal](https://developer.twitter.com/)
3. **Telegram Bot**: Create bot with [@BotFather](https://t.me/botfather)

## 📊 Usage

### 1. Sentiment Analysis

```python
import requests

# Analyze single text
response = requests.post(
    "http://localhost:8080/api/v1/sentiment/analyze",
    json={"text": "Apple stock is performing exceptionally well", "model": "finbert"}
)
result = response.json()
print(f"Sentiment: {result['data']['sentiment']}")
print(f"Confidence: {result['data']['confidence']}")
```

### 2. Generate Trading Signals

```python
# Generate signals for multiple symbols
response = requests.post(
    "http://localhost:8080/api/v1/signals/generate",
    json={"symbols": ["AAPL", "GOOGL", "MSFT"], "timeframe": "1d", "lookback": 7}
)
signals = response.json()["data"]

for signal in signals:
    print(f"{signal['symbol']}: {signal['action']} (confidence: {signal['confidence']})")
```

### 3. Fetch News Data

```python
# Fetch recent news
response = requests.post(
    "http://localhost:8080/api/v1/news/fetch",
    json={"query": "Apple stock", "page_size": 10}
)
news = response.json()["data"]["articles"]

for article in news:
    print(f"{article['title']} - {article['source']}")
```

## 🧪 Testing

### Run Test Suite

```bash
# Python tests
cd /path/to/project
python -m pytest tests/ -v

# Go tests
cd golang-api
go test ./... -v

# Integration tests
docker-compose exec go-api go test ./... -v
```

### Test Coverage

```bash
# Python coverage
python -m pytest tests/ --cov=src --cov-report=html

# Go coverage
cd golang-api
go test ./... -cover
```

## 📈 Monitoring

### Access Monitoring Dashboards

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **API Health**: http://localhost:8080/api/v1/health

### Key Metrics

- API response times
- Model inference performance
- Database query performance
- Signal accuracy rates
- System resource usage

## 🔬 Research Features

### Model Comparison

The system supports multiple sentiment analysis models:

- **FinBERT**: Financial domain-specific BERT model
- **RoBERTa**: Robustly optimized BERT approach
- **DistilBERT**: Distilled BERT for faster inference

### Performance Metrics

- Accuracy, Precision, Recall, F1-Score
- Signal accuracy over time
- Backtesting results
- Risk-adjusted returns (Sharpe ratio)
- Maximum drawdown analysis

### Data Sources

- **News**: Reuters, Bloomberg, Yahoo Finance, NewsAPI
- **Social Media**: Twitter, Reddit
- **Market Data**: Yahoo Finance, Alpha Vantage
- **Economic Indicators**: Federal Reserve, Bureau of Labor Statistics

## 📚 API Documentation

Comprehensive API documentation is available at:
- **Swagger UI**: http://localhost:8080/docs (when implemented)
- **API Docs**: [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)

### Key Endpoints

- `POST /api/v1/sentiment/analyze` - Analyze sentiment
- `POST /api/v1/signals/generate` - Generate trading signals
- `GET /api/v1/news` - Retrieve news data
- `GET /api/v1/signals/performance` - Get performance metrics

## 🛠️ Development

### Local Development Setup

```bash
# Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Go environment
cd golang-api
go mod download
go run main.go

# Start ML service
python src/ml_service.py
```

### Code Quality

```bash
# Python linting
flake8 src/
black src/
isort src/

# Go formatting
gofmt -w .
go vet ./...
```

## 📊 Performance

### Benchmarks

- **Sentiment Analysis**: ~100ms per text (FinBERT)
- **Batch Processing**: ~50 texts/second
- **Signal Generation**: ~200ms per symbol
- **Database Queries**: <10ms average response time

### Scalability

- Horizontal scaling with Docker Swarm/Kubernetes
- Redis caching for improved performance
- Database connection pooling
- Asynchronous processing for large datasets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-username/ai-sentiment-market-prediction/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/ai-sentiment-market-prediction/discussions)

## 🙏 Acknowledgments

- **FinBERT**: [ProsusAI/finbert](https://huggingface.co/ProsusAI/finbert)
- **Transformers**: [Hugging Face](https://huggingface.co/transformers/)
- **yfinance**: [yfinance](https://github.com/ranaroussi/yfinance)
- **NewsAPI**: [NewsAPI.org](https://newsapi.org/)

## 📈 Roadmap

- [ ] Real-time streaming data processing
- [ ] Advanced ensemble models
- [ ] WebSocket API for real-time updates
- [ ] Mobile application
- [ ] Advanced backtesting framework
- [ ] Multi-asset portfolio optimization
- [ ] Integration with trading platforms

---

**Built with ❤️ for academic research and financial market analysis**