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

from ml_service.sentiment import get_analyzer, FinBERTAnalyzer
from ml_service.indicators import get_indicators, TechnicalIndicators
from ml_service.hybrid_engine import get_engine, HybridEngine

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
analyzer = get_analyzer()
indicators = get_indicators()
engine = get_engine()

# Pydantic models
class SentimentRequest(BaseModel):
    text: str = Field(..., description="Text to analyze for sentiment")
    
class SentimentResponse(BaseModel):
    label: str
    score: float
    confidence: float
    model: str

class TechnicalRequest(BaseModel):
    symbol: str = Field(..., description="Trading symbol")
    period: Optional[str] = Field("7d", description="Time period for data")

class TechnicalResponse(BaseModel):
    ema20: Optional[float]
    ema50: Optional[float]
    rsi: Optional[float]
    macd: Optional[float]
    technical_score: float

class HybridRequest(BaseModel):
    sentiment_score: float = Field(..., ge=0, le=1, description="Sentiment score")
    technical_score: float = Field(..., ge=0, le=1, description="Technical score")
    sentiment_confidence: Optional[float] = Field(1.0, ge=0, le=1, description="Sentiment confidence")
    technical_confidence: Optional[float] = Field(1.0, ge=0, le=1, description="Technical confidence")

class HybridResponse(BaseModel):
    signal: str
    hybrid_score: float
    confidence: float
    reason: str
    sentiment_score: float
    technical_score: float

class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str
    models_loaded: bool

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
            "sentiment": "/sentiment/analyze",
            "technical": "/technical/calculate",
            "hybrid": "/hybrid/generate"
        }
    }

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="ML Service",
        timestamp=datetime.now().isoformat(),
        models_loaded=True
    )

# Sentiment analysis endpoint
@app.post("/sentiment/analyze", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest):
    """
    Analyze sentiment of text using FinBERT
    
    Args:
        request: Sentiment request with text
        
    Returns:
        Sentiment analysis result
    """
    try:
        result = analyzer.analyze(request.text)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return SentimentResponse(
            label=result["label"],
            score=result["score"],
            confidence=result["confidence"],
            model=result.get("model", "finbert")
        )
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
@app.post("/technical/calculate", response_model=TechnicalResponse)
async def calculate_technical(request: TechnicalRequest):
    """
    Calculate technical indicators (placeholder - requires market data)
    
    Args:
        request: Technical request with symbol
        
    Returns:
        Technical indicators result
    """
    try:
        # This is a placeholder
        # In production, this would fetch market data and calculate indicators
        logger.info(f"Calculating technical indicators for {request.symbol}")
        
        # Return mock data for now
        # TODO: Integrate with actual market data fetching
        return TechnicalResponse(
            ema20=None,
            ema50=None,
            rsi=None,
            macd=None,
            technical_score=0.5
        )
    except Exception as e:
        logger.error(f"Error calculating technical indicators: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Hybrid signal generation endpoint
@app.post("/hybrid/generate", response_model=HybridResponse)
async def generate_hybrid_signal(request: HybridRequest):
    """
    Generate hybrid trading signal
    
    Args:
        request: Hybrid request with sentiment and technical scores
        
    Returns:
        Hybrid signal result
    """
    try:
        result = engine.generate_signal(
            sentiment_score=request.sentiment_score,
            technical_score=request.technical_score,
            sentiment_confidence=request.sentiment_confidence,
            technical_confidence=request.technical_confidence
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return HybridResponse(
            signal=result["signal"],
            hybrid_score=result["hybrid_score"],
            confidence=result["confidence"],
            reason=result["reason"],
            sentiment_score=result["sentiment_score"],
            technical_score=result["technical_score"]
        )
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

