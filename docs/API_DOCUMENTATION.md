# AI Sentiment Market Prediction - API Documentation

## Overview

The AI Sentiment Market Prediction system provides a comprehensive API for sentiment analysis, trading signal generation, and market data collection. This system is designed for academic research and dissertation purposes.

## Base URLs

- **Go Backend API**: `http://localhost:8080/api/v1`
- **Python ML Service**: `http://localhost:8000`

## Authentication

Currently, the API does not require authentication. For production use, implement JWT-based authentication.

## Endpoints

### Health Check

#### GET /api/v1/health

Check the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "service": "ai-sentiment-market-prediction",
  "version": "1.0.0"
}
```

### Sentiment Analysis

#### POST /api/v1/sentiment/analyze

Analyze sentiment of a single text.

**Request Body:**
```json
{
  "text": "Apple stock is performing exceptionally well this quarter",
  "model": "finbert"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "sentiment": "POSITIVE",
    "confidence": 0.89,
    "model": "finbert",
    "text": "Apple stock is performing exceptionally well this quarter"
  }
}
```

#### GET /api/v1/sentiment/batch

Get batch sentiment analysis results.

**Query Parameters:**
- `model` (optional): Model to use (default: finbert)
- `limit` (optional): Number of results to return (default: 100)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "sentiment": "POSITIVE",
      "confidence": 0.89,
      "model": "finbert",
      "text": "Sample text"
    }
  ],
  "model": "finbert",
  "limit": 100
}
```

#### GET /api/v1/sentiment/models

Get available sentiment analysis models.

**Response:**
```json
{
  "models": ["finbert", "roberta", "distilbert"],
  "count": 3
}
```

#### GET /api/v1/sentiment/models/{model_name}/performance

Get performance metrics for a specific model.

**Response:**
```json
{
  "accuracy": 0.85,
  "precision": 0.82,
  "recall": 0.88,
  "f1_score": 0.85,
  "total_predictions": 1000,
  "correct_predictions": 850,
  "model_name": "finbert",
  "last_updated": "2024-01-01T00:00:00Z"
}
```

### Trading Signals

#### GET /api/v1/signals

Get existing trading signals.

**Query Parameters:**
- `symbol` (optional): Stock symbol to filter by
- `limit` (optional): Number of signals to return (default: 50)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "symbol": "AAPL",
      "action": "BUY",
      "strength": 0.85,
      "confidence": 0.78,
      "reasoning": "Strong positive sentiment suggests bullish momentum",
      "sentiment_score": 0.82,
      "price_target": 185.50,
      "stop_loss": 175.20,
      "created_at": "2024-01-01T10:00:00Z",
      "expires_at": "2024-01-02T10:00:00Z"
    }
  ],
  "count": 1
}
```

#### POST /api/v1/signals/generate

Generate new trading signals.

**Request Body:**
```json
{
  "symbols": ["AAPL", "GOOGL", "MSFT"],
  "timeframe": "1d",
  "lookback": 7
}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "symbol": "AAPL",
      "action": "BUY",
      "strength": 0.85,
      "confidence": 0.78,
      "reasoning": "Strong positive sentiment suggests bullish momentum",
      "sentiment_score": 0.82,
      "price_target": 185.50,
      "stop_loss": 175.20,
      "created_at": "2024-01-01T10:00:00Z",
      "expires_at": "2024-01-02T10:00:00Z"
    }
  ],
  "count": 3,
  "generated_at": "2024-01-01T10:00:00Z"
}
```

#### GET /api/v1/signals/performance

Get performance metrics for trading signals.

**Query Parameters:**
- `symbol` (optional): Stock symbol to filter by
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format

**Response:**
```json
{
  "success": true,
  "data": {
    "metrics": {
      "symbol": "AAPL",
      "total_signals": 100,
      "correct_signals": 85,
      "accuracy": 0.85,
      "total_return": 0.12,
      "sharpe_ratio": 1.45,
      "max_drawdown": 0.08,
      "win_rate": 0.75,
      "average_return": 0.0015,
      "volatility": 0.18,
      "start_date": "2024-01-01T00:00:00Z",
      "end_date": "2024-01-31T23:59:59Z",
      "created_at": "2024-01-31T23:59:59Z"
    },
    "recent_signals": [...],
    "chart_data": [...]
  },
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }
}
```

#### GET /api/v1/signals/accuracy

Get signal accuracy for a specific period.

**Query Parameters:**
- `symbol` (optional): Stock symbol to filter by
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format

**Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "accuracy": 0.85,
    "period": {
      "start_date": "2024-01-01",
      "end_date": "2024-01-31"
    }
  }
}
```

### News Data

#### GET /api/v1/news

Get stored news articles.

**Query Parameters:**
- `symbol` (optional): Stock symbol to filter by
- `limit` (optional): Number of articles to return (default: 50)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "Apple Reports Strong Q4 Earnings",
      "content": "Apple Inc. reported better-than-expected earnings...",
      "source": "Reuters",
      "url": "https://reuters.com/apple-earnings",
      "published_at": "2024-01-01T10:00:00Z",
      "created_at": "2024-01-01T10:05:00Z",
      "updated_at": "2024-01-01T10:05:00Z"
    }
  ],
  "count": 1
}
```

#### POST /api/v1/news/fetch

Fetch news articles from external sources.

**Request Body:**
```json
{
  "query": "Apple stock",
  "sources": "reuters,bloomberg",
  "from": "2024-01-01",
  "to": "2024-01-31",
  "sort_by": "publishedAt",
  "page_size": 20,
  "page": 1
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "articles": [...],
    "total": 150,
    "page": 1,
    "page_size": 20
  },
  "fetched_at": "2024-01-01T10:00:00Z"
}
```

#### GET /api/v1/news/search

Search news articles using full-text search.

**Query Parameters:**
- `q` (required): Search query
- `limit` (optional): Number of results to return (default: 20)

**Response:**
```json
{
  "success": true,
  "data": [...],
  "query": "Apple earnings",
  "count": 15
}
```

#### GET /api/v1/news/date-range

Get news articles within a date range.

**Query Parameters:**
- `start_date` (required): Start date in YYYY-MM-DD format
- `end_date` (required): End date in YYYY-MM-DD format
- `symbol` (optional): Stock symbol to filter by

**Response:**
```json
{
  "success": true,
  "data": [...],
  "count": 25,
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }
}
```

#### GET /api/v1/news/sources

Get available news sources.

**Response:**
```json
{
  "success": true,
  "data": ["Reuters", "Bloomberg", "CNN", "BBC", "Financial Times"],
  "count": 5
}
```

## Python ML Service Endpoints

### GET /

Get service information.

**Response:**
```json
{
  "service": "AI Sentiment Market Prediction - ML Service",
  "version": "1.0.0",
  "status": "healthy",
  "available_models": ["finbert", "roberta", "distilbert"]
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T10:00:00Z",
  "models_loaded": 3,
  "device": "cuda"
}
```

### POST /analyze

Analyze sentiment of a single text.

**Request Body:**
```json
{
  "text": "Apple stock is performing well",
  "model": "finbert"
}
```

**Response:**
```json
{
  "sentiment": "POSITIVE",
  "confidence": 0.89,
  "model": "finbert",
  "text": "Apple stock is performing well"
}
```

### POST /analyze_batch

Analyze sentiment of multiple texts.

**Request Body:**
```json
{
  "texts": ["Text 1", "Text 2", "Text 3"],
  "model": "finbert"
}
```

**Response:**
```json
[
  {
    "sentiment": "POSITIVE",
    "confidence": 0.89,
    "model": "finbert",
    "text": "Text 1"
  },
  {
    "sentiment": "NEGATIVE",
    "confidence": 0.76,
    "model": "finbert",
    "text": "Text 2"
  }
]
```

### GET /models

Get available models.

**Response:**
```json
{
  "models": ["finbert", "roberta", "distilbert"],
  "count": 3
}
```

### GET /models/{model_name}/info

Get model information.

**Response:**
```json
{
  "name": "finbert",
  "description": "Financial sentiment analysis model",
  "accuracy": 0.85,
  "precision": 0.82,
  "recall": 0.88,
  "f1_score": 0.85,
  "training_date": "2024-01-01",
  "dataset_size": 10000
}
```

### GET /models/{model_name}/performance

Get model performance metrics.

**Response:**
```json
{
  "accuracy": 0.85,
  "precision": 0.82,
  "recall": 0.88,
  "f1_score": 0.85,
  "total_predictions": 1000,
  "correct_predictions": 850,
  "model_name": "finbert",
  "last_updated": "2024-01-01T00:00:00Z"
}
```

### GET /stats

Get service statistics.

**Response:**
```json
{
  "total_models": 3,
  "available_models": ["finbert", "roberta", "distilbert"],
  "device": "cuda",
  "service_uptime": "2 days, 5 hours",
  "last_updated": "2024-01-01T10:00:00Z"
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "error": "Invalid request format",
  "details": "Field 'text' is required"
}
```

### 404 Not Found
```json
{
  "error": "Model not found",
  "details": "Model 'invalid_model' not available"
}
```

### 500 Internal Server Error
```json
{
  "error": "Failed to analyze sentiment",
  "details": "Model loading failed"
}
```

## Rate Limiting

- **Default**: 100 requests per minute per IP
- **Burst**: 200 requests per minute
- **Headers**: Rate limit information is included in response headers

## CORS

The API supports CORS for the following origins:
- `http://localhost:3000`
- `http://localhost:8080`

## Examples

### cURL Examples

#### Analyze Sentiment
```bash
curl -X POST "http://localhost:8080/api/v1/sentiment/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "Apple stock is performing well", "model": "finbert"}'
```

#### Generate Trading Signals
```bash
curl -X POST "http://localhost:8080/api/v1/signals/generate" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "GOOGL"], "timeframe": "1d", "lookback": 7}'
```

#### Fetch News
```bash
curl -X POST "http://localhost:8080/api/v1/news/fetch" \
  -H "Content-Type: application/json" \
  -d '{"query": "Apple stock", "page_size": 10}'
```

### Python Examples

#### Analyze Sentiment
```python
import requests

response = requests.post(
    "http://localhost:8080/api/v1/sentiment/analyze",
    json={"text": "Apple stock is performing well", "model": "finbert"}
)
result = response.json()
print(result["data"]["sentiment"])
```

#### Generate Signals
```python
import requests

response = requests.post(
    "http://localhost:8080/api/v1/signals/generate",
    json={"symbols": ["AAPL", "GOOGL"], "timeframe": "1d", "lookback": 7}
)
signals = response.json()["data"]
for signal in signals:
    print(f"{signal['symbol']}: {signal['action']} (confidence: {signal['confidence']})")
```

## Support

For questions or issues, please refer to the project documentation or create an issue in the repository.
