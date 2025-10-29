"""
FastAPI Main Application for ML Service
Provides sentiment analysis, technical indicators, and hybrid decision engine endpoints
"""

import logging
from typing import List, Optional
from datetime import datetime
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ml_service.sentiment import get_analyzer, FinBERTAnalyzer, get_db_manager as get_sentiment_db
from ml_service.indicators import get_indicators, TechnicalIndicators, get_db_manager as get_technical_db
from ml_service.hybrid_engine import get_engine, HybridEngine, get_db_manager as get_hybrid_db

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Sentiment Market Prediction - ML Service",
    description="Machine Learning service for sentiment analysis and technical indicators",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzers
try:
    analyzer = get_analyzer()
    indicators = get_indicators()
    engine = get_engine(sentiment_weight=0.6, technical_weight=0.4)  # α=0.6, β=0.4
    sentiment_db = get_sentiment_db()
    technical_db = get_technical_db()
    hybrid_db = get_hybrid_db()
    logger.info("All ML components initialized successfully")
except Exception as e:
    logger.error(f"Error initializing ML components: {e}")
    analyzer = None
    indicators = None
    engine = None
    sentiment_db = None
    technical_db = None
    hybrid_db = None

# Pydantic models
class SentimentRequest(BaseModel):
    symbol: str = Field(..., description="Trading symbol (e.g., AAPL, BTCUSDT)")
    text: str = Field(..., description="Text to analyze for sentiment")
    
class SentimentBatchRequest(BaseModel):
    """Request model for batch sentiment analysis"""
    texts: List[str] = Field(..., description="List of texts to analyze")
    
class SentimentResponse(BaseModel):
    """Response model for sentiment analysis"""
    symbol: str
    label: str
    sentiment_score: float
    confidence: float

class TechnicalRequest(BaseModel):
    """Request model for technical analysis"""
    symbol: str = Field(..., description="Trading symbol (e.g., AAPL, BTC-USD, ETH-USD)")
    period: Optional[str] = Field("3mo", description="Time period for data (e.g., 1d, 5d, 1mo, 3mo, 1y)")

class TechnicalResponse(BaseModel):
    """Response model for technical indicators"""
    symbol: str
    ema20: Optional[float]
    ema50: Optional[float]
    rsi: Optional[float]
    macd: Optional[float]
    technical_score: float

class HybridRequest(BaseModel):
    """Request model for hybrid signal generation"""
    symbol: str = Field(..., description="Trading symbol (e.g., AAPL, BTC-USD)")
    
class HybridResponse(BaseModel):
    """Response model for hybrid signals"""
    symbol: str
    sentiment_score: Optional[float]
    technical_score: Optional[float]
    hybrid_score: float
    signal: str
    confidence: float
    reason: str

class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str
    models_loaded: bool
    sentiment_db_connected: bool
    technical_db_connected: bool
    hybrid_db_connected: bool

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "AI Sentiment Market Prediction - ML Service",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "sentiment": "/sentiment",
            "technical": "/technical",
            "hybrid": "/hybrid"
        }
    }

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns service status and component health
    """
    return HealthResponse(
        status="ok",
        service="ML Service",
        timestamp=datetime.now().isoformat(),
        models_loaded=analyzer is not None,
        sentiment_db_connected=sentiment_db is not None,
        technical_db_connected=technical_db is not None,
        hybrid_db_connected=hybrid_db is not None
    )

# Sentiment analysis endpoint
@app.post("/sentiment", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest):
    """
    Analyze sentiment of financial text using FinBERT and save to database
    
    Input: {"symbol": "AAPL", "text": "Apple shares jump after record iPhone sales"}
    Output: {"symbol": "AAPL", "label": "positive", "sentiment_score": 0.82, "confidence": 0.91}
    
    Args:
        request: Sentiment request with symbol and text
        
    Returns:
        Sentiment analysis result with database persistence
    """
    if analyzer is None:
        raise HTTPException(status_code=503, detail="ML service not initialized")
    
    try:
        # Analyze sentiment using FinBERT
        result = analyzer.analyze(request.text)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Prepare response with symbol
        response_data = {
            "symbol": request.symbol,
            "label": result["label"],
            "sentiment_score": result["sentiment_score"],
            "confidence": result["confidence"]
        }
        
        # Save to database if available
        if sentiment_db:
            try:
                sentiment_db.save_sentiment_result(
                    symbol=request.symbol,
                    sentiment_score=result["sentiment_score"],
                    label=result["label"],
                    confidence=result["confidence"]
                )
            except Exception as db_error:
                logger.warning(f"Could not save to sentiment database: {db_error}")
        
        return SentimentResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Batch sentiment analysis endpoint
@app.post("/sentiment/analyze_batch")
async def analyze_sentiment_batch(texts: List[str]):
    """
    Analyze sentiment of multiple texts
    
    Args:
        texts: List of texts to analyze
        
    Returns:
        List of sentiment analysis results
    """
    try:
        results = analyzer.analyze_batch(texts)
        return {
            "success": True,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error in batch sentiment analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Technical indicators endpoint
@app.post("/technical", response_model=TechnicalResponse)
async def calculate_technical(request: TechnicalRequest):
    """
    Calculate technical indicators using yfinance and pandas-ta
    
    Input: {"symbol": "AAPL", "period": "3mo"}
    Output: {"symbol": "AAPL", "ema20": 175.32, "ema50": 172.80, "rsi": 64.5, "macd": 1.32, "technical_score": 0.72}
    
    Technical Score Range: -1.0 to +1.0
    - Negative = Bearish
    - Positive = Bullish
    - 0 = Neutral
    
    Args:
        request: Technical request with symbol and optional period
        
    Returns:
        Technical indicators result with database persistence
    """
    if indicators is None:
        raise HTTPException(status_code=503, detail="ML service not initialized")
    
    try:
        logger.info(f"Calculating technical indicators for {request.symbol}")
        
        # Calculate technical indicators
        result = indicators.analyze(request.symbol, period=request.period)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Save to database if available
        if technical_db and result['ema20'] is not None:
            try:
                technical_db.save_technical_indicators(
                    symbol=result['symbol'],
                    ema20=result['ema20'],
                    ema50=result['ema50'],
                    rsi=result['rsi'],
                    macd=result['macd'],
                    technical_score=result['technical_score']
                )
            except Exception as db_error:
                logger.warning(f"Could not save to technical database: {db_error}")
        
        return TechnicalResponse(
            symbol=result['symbol'],
            ema20=result['ema20'],
            ema50=result['ema50'],
            rsi=result['rsi'],
            macd=result['macd'],
            technical_score=result['technical_score']
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating technical indicators: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Hybrid signal generation endpoint
@app.post("/hybrid", response_model=HybridResponse)
async def generate_hybrid_signal(request: HybridRequest):
    """
    Generate hybrid trading signal by combining sentiment and technical analysis
    
    Input: {"symbol": "AAPL"}
    Output: {
        "symbol": "AAPL",
        "sentiment_score": 0.74,
        "technical_score": 0.42,
        "hybrid_score": 0.62,
        "signal": "BUY",
        "confidence": 0.85,
        "reason": "Positive sentiment and bullish EMA/RSI"
    }
    
    Hybrid Score Thresholds:
    - > 0.3  → BUY (bullish momentum)
    - < -0.3 → SELL (bearish momentum)
    - else   → HOLD (neutral)
    
    Args:
        request: Hybrid request with symbol
        
    Returns:
        Hybrid signal result with database persistence
    """
    if engine is None or hybrid_db is None:
        raise HTTPException(status_code=503, detail="ML service or database not initialized")
    
    try:
        logger.info(f"Generating hybrid signal for {request.symbol}")
        
        # Analyze symbol using hybrid engine
        result = engine.analyze_symbol(request.symbol, hybrid_db.conn)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Save to database if we have valid data
        if result.get('sentiment_score') is not None or result.get('technical_score') is not None:
            try:
                hybrid_db.save_hybrid_signal(
                    symbol=result['symbol'],
                    sentiment_score=result['sentiment_score'] or 0.0,
                    technical_score=result['technical_score'] or 0.0,
                    hybrid_score=result['hybrid_score'],
                    signal=result['signal'],
                    reason=result['reason'],
                    confidence=result['confidence']
                )
            except Exception as db_error:
                logger.warning(f"Could not save to hybrid database: {db_error}")
        
        return HybridResponse(
            symbol=result['symbol'],
            sentiment_score=result.get('sentiment_score'),
            technical_score=result.get('technical_score'),
            hybrid_score=result['hybrid_score'],
            signal=result['signal'],
            confidence=result['confidence'],
            reason=result['reason']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating hybrid signal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Engine configuration endpoint
@app.post("/engine/configure")
async def configure_engine(sentiment_weight: float, technical_weight: float):
    """
    Configure hybrid engine weights
    
    Args:
        sentiment_weight: Weight for sentiment analysis
        technical_weight: Weight for technical indicators
    """
    try:
        engine.adjust_weights(sentiment_weight, technical_weight)
        return {
            "success": True,
            "sentiment_weight": sentiment_weight,
            "technical_weight": technical_weight
        }
    except Exception as e:
        logger.error(f"Error configuring engine: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

