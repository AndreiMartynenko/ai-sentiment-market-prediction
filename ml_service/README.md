# ML Service Documentation

## Overview

The ML Service provides sentiment analysis, technical indicators, and hybrid decision-making for the AI-Driven Sentiment Market Prediction System.

## Sentiment Analysis Module

### FinBERT Implementation

**File**: `sentiment.py`

**Model**: `yiyanghkust/finbert-tone`

**Features**:
- Financial domain-specific sentiment analysis
- 3-class classification (positive, negative, neutral)
- Sentiment scoring in range -1.0 to +1.0
- Confidence scoring (max probability)
- PostgreSQL integration for result persistence
- Batch processing support

### Usage Examples

#### Python Direct Usage

```python
from ml_service.sentiment import get_analyzer

# Initialize analyzer
analyzer = get_analyzer()

# Analyze single text
result = analyzer.analyze("Apple shares jump after record iPhone sales")
print(result)
# Output: {'label': 'positive', 'sentiment_score': 0.82, 'confidence': 0.91}
```

#### FastAPI Endpoint

**Request**:
```bash
curl -X POST http://localhost:8000/sentiment \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "text": "Apple shares jump after record iPhone sales"}'
```

**Response**:
```json
{
  "symbol": "AAPL",
  "label": "positive",
  "sentiment_score": 0.82,
  "confidence": 0.91
}
```

### Sentiment Score Range

- **Positive sentiment**: Score ranges from 0.0 to +1.0
- **Negative sentiment**: Score ranges from 0.0 to -1.0
- **Neutral sentiment**: Score ≈ 0.0

### Confidence Score

Confidence is the maximum probability from the softmax output:
- High confidence (0.8-1.0): Model is very certain
- Medium confidence (0.5-0.8): Model is somewhat certain
- Low confidence (<0.5): Model is uncertain

### Database Integration

Results are automatically saved to the `sentiment_results` table:

```sql
INSERT INTO sentiment_results (symbol, sentiment_score, label, confidence, timestamp)
VALUES ('AAPL', 0.82, 'positive', 0.91, NOW());
```

## Technical Indicators Module

**File**: `indicators.py`

Calculates EMA, RSI, and MACD using pandas-ta.

## Hybrid Decision Engine

**File**: `hybrid_engine.py`

Combines sentiment and technical analysis to generate trading signals.

## Running the Service

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn ml_service.main:app --reload --host 0.0.0.0 --port 8000
```

### Production (Docker)

```bash
# Build and run with Docker Compose
docker-compose up -d ml-service

# View logs
docker-compose logs -f ml-service
```

## Testing

### Test the Module

```bash
python ml_service/sentiment.py
```

### Test the API

```bash
python test_sentiment_api.py
```

## Endpoints

- `GET /health` - Health check
- `POST /sentiment` - Analyze sentiment with database persistence
- `POST /technical/calculate` - Calculate technical indicators
- `POST /hybrid/generate` - Generate hybrid trading signals

## Environment Variables

- `DB_HOST`: PostgreSQL host (default: postgres)
- `POSTGRES_USER`: Database user (default: postgres)
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name (default: sentiment_market)
- `POSTGRES_PORT`: Database port (default: 5432)

## Model Details

### FinBERT Architecture

- **Base Model**: BERT
- **Fine-tuning**: Financial text (news, reports, social media)
- **Classes**: 3 (positive, negative, neutral)
- **Max Sequence Length**: 512 tokens
- **Inference Device**: CUDA (if available) or CPU

### Model Loading

The model is downloaded from Hugging Face on first use and cached locally.

## Performance

- **Single inference**: ~100ms (CPU), ~50ms (GPU)
- **Batch processing**: ~50 texts/second
- **Memory usage**: ~500MB

## Troubleshooting

### Model Loading Issues

If the model fails to load:
1. Check internet connection (first-time download)
2. Verify Hugging Face access
3. Check disk space
4. Review logs for specific error messages

### Database Connection Issues

If database connection fails:
1. Verify PostgreSQL is running
2. Check connection credentials in environment variables
3. Ensure network access from service to database
4. Review database logs

### CUDA Issues

If CUDA is not available:
- Service will automatically fall back to CPU
- Performance will be slower but functional
- Check CUDA installation if GPU is expected

