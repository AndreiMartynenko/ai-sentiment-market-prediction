"""
FastAPI Main Application for ML Service (No Database Version)
Simplified version that works without PostgreSQL
"""

import logging
from typing import List, Optional
from datetime import datetime
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ml_service.sentiment import get_analyzer
from ml_service.indicators import get_indicators
from ml_service.hybrid_engine import get_engine
from ml_service.solana_layer import send_proof
from ml_service.news import get_crypto_news_manager
from ml_service.crypto_data import get_crypto_data_manager
from ml_service.institutional_signal import generate_institutional_signal, generate_institutional_signal_debug

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global managers
news_manager = None
# Initialize FastAPI app
app = FastAPI(
    title="AI Sentiment Market Prediction - ML Service (No DB)",
    description="Machine Learning service for sentiment analysis and technical indicators (No database required)",
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

# Initialize analyzers (no database managers)
try:
    analyzer = get_analyzer()
    indicators = get_indicators()
    engine = get_engine(sentiment_weight=0.5, technical_weight=0.3)
    news_manager = get_crypto_news_manager(analyzer)
    logger.info("All ML components initialized successfully (No database mode)")
except Exception as e:
    logger.error(f"Error initializing ML components: {e}")
    analyzer = None
    indicators = None
    engine = None
    news_manager = None

# Pydantic models
class SentimentRequest(BaseModel):
    symbol: str = Field(..., description="Trading symbol (e.g., BTCUSDT)")
    text: str = Field(..., description="Text to analyze for sentiment")
    
class SentimentResponse(BaseModel):
    symbol: str
    label: str
    sentiment_score: float
    confidence: float

class TechnicalRequest(BaseModel):
    symbol: str = Field(..., description="Trading symbol (e.g., BTCUSDT)")
    period: Optional[str] = Field("3mo", description="Time period for data")

class TechnicalResponse(BaseModel):
    symbol: str
    ema20: Optional[float]
    ema50: Optional[float]
    rsi: Optional[float]
    macd: Optional[float]
    technical_score: float

class HybridRequest(BaseModel):
    symbol: str = Field(..., description="Trading symbol (e.g., BTCUSDT)")

class HybridResponse(BaseModel):
    symbol: str
    sentiment_score: Optional[float]
    technical_score: Optional[float]
    volatility_index: Optional[float]
    hybrid_score: float
    signal: str
    confidence: float
    reason: str
    proof_hash: Optional[str] = None
    tx_signature: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str
    models_loaded: bool

class NewsItem(BaseModel):
    title: str
    url: Optional[str]
    published_at: Optional[str]
    source: Optional[str]
    domain: Optional[str]
    sentiment_label: str
    sentiment_score: float
    sentiment_confidence: float

class SymbolNews(BaseModel):
    symbol: str
    items: List[NewsItem]

class NewsResponse(BaseModel):
    success: bool
    symbols: List[str]
    data: List[SymbolNews]
    source: str
    last_updated: str

class InstitutionalSignalRequest(BaseModel):
    symbol: str = Field(..., description="Trading symbol (e.g., BTCUSDT)")
    timeframe: Optional[str] = Field("15m", description="Execution timeframe: 5m, 15m, or 1h")
    use_sentiment: Optional[bool] = Field(False, description="Enable strict news sentiment gating")

# In-memory signal storage (optional, for listing)
signals_cache = []

DEFAULT_NEWS_SYMBOLS = [
    "BTC", "ETH", "SOL", "BNB", "ADA", "XRP", "DOGE", "AVAX", "DOT", "MATIC",
    "TON", "FET", "RNDR", "NEAR", "UNI", "AAVE", "COMP", "ARB", "OP", "USDT", "USDC"
]

# Root endpoint
@app.get("/")
async def root():
    return {
        "service": "AI Sentiment Market Prediction - ML Service (No DB)",
        "version": "1.0.0",
        "status": "operational",
        "mode": "no_database",
        "endpoints": {
            "health": "/health",
            "sentiment": "/sentiment",
            "technical": "/technical",
            "hybrid": "/hybrid",
            "signals_list": "/signals/list",
            "news": "/news/crypto"
        }
    }

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="ok",
        service="ML Service (No DB)",
        timestamp=datetime.now().isoformat(),
        models_loaded=analyzer is not None and indicators is not None and engine is not None
    )

# Sentiment analysis endpoint (no database saving)
@app.post("/sentiment", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest):
    if analyzer is None:
        raise HTTPException(status_code=503, detail="ML service not initialized")
    
    try:
        result = analyzer.analyze(request.text)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return SentimentResponse(
            symbol=request.symbol,
            label=result["label"],
            sentiment_score=result["sentiment_score"],
            confidence=result["confidence"]
        )
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/signal/institutional")
async def institutional_signal(request: InstitutionalSignalRequest):
    """Institutional-grade signal endpoint (strict NO_TRADE-by-default)."""
    try:
        timeframe = (request.timeframe or "15m").strip()
        if timeframe not in {"5m", "15m", "1h"}:
            raise HTTPException(status_code=400, detail="Invalid timeframe. Use 5m, 15m, or 1h.")

        data_manager = get_crypto_data_manager()
        if request.use_sentiment:
            result, _debug = generate_institutional_signal_debug(
                symbol=request.symbol,
                data_manager=data_manager,
                news_manager=news_manager,
                timeframe=timeframe,
                use_sentiment=True,
            )
        else:
            result = generate_institutional_signal(
                symbol=request.symbol,
                data_manager=data_manager,
                news_manager=news_manager,
                timeframe=timeframe,
            )

        # Strict output requirement: only JSON (FastAPI returns dict as JSON)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating institutional signal: {e}")
        return {"signal": "NO_TRADE", "reason": "insufficient confluence"}


@app.post("/signal/institutional/debug")
async def institutional_signal_debug(request: InstitutionalSignalRequest):
    """Debug version of the institutional signal endpoint (includes gate diagnostics)."""
    try:
        timeframe = (request.timeframe or "15m").strip()
        if timeframe not in {"5m", "15m", "1h"}:
            raise HTTPException(status_code=400, detail="Invalid timeframe. Use 5m, 15m, or 1h.")

        data_manager = get_crypto_data_manager()
        result, debug = generate_institutional_signal_debug(
            symbol=request.symbol,
            data_manager=data_manager,
            news_manager=news_manager,
            timeframe=timeframe,
            use_sentiment=bool(request.use_sentiment),
        )

        return {"result": result, "debug": debug}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating institutional signal debug: {e}")
        return {
            "result": {"signal": "NO_TRADE", "reason": "insufficient confluence"},
            "debug": {"error": str(e)},
        }

# Technical indicators endpoint (no database saving)
@app.post("/technical", response_model=TechnicalResponse)
async def calculate_technical(request: TechnicalRequest):
    if indicators is None:
        raise HTTPException(status_code=503, detail="ML service not initialized")
    
    try:
        result = indicators.analyze(request.symbol, period=request.period)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return TechnicalResponse(
            symbol=result['symbol'],
            ema20=result.get('ema20'),
            ema50=result.get('ema50'),
            rsi=result.get('rsi'),
            macd=result.get('macd'),
            technical_score=result['technical_score']
        )
    except Exception as e:
        logger.error(f"Error calculating technical indicators: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# News endpoint
@app.get("/news/crypto", response_model=NewsResponse)
async def get_crypto_news(symbols: Optional[str] = None, limit: int = 10):
    """Fetch crypto news with sentiment analysis for specified symbols."""
    if news_manager is None:
        raise HTTPException(status_code=503, detail="News service not initialized")

    try:
        if symbols:
            symbol_list = [sym.strip().upper() for sym in symbols.split(',') if sym.strip()]
        else:
            symbol_list = DEFAULT_NEWS_SYMBOLS

        if not symbol_list:
            raise HTTPException(status_code=400, detail="No symbols provided")

        limit = max(1, min(limit, 20))
        raw_news = news_manager.fetch_news_for_symbols(symbol_list, limit)

        news_payload: List[SymbolNews] = []
        for symbol in symbol_list:
            items_payload: List[NewsItem] = []
            for item in raw_news.get(symbol, []):
                sentiment = item.get("sentiment", {}) or {}
                items_payload.append(
                    NewsItem(
                        title=item.get("title", ""),
                        url=item.get("url"),
                        published_at=item.get("published_at"),
                        source=item.get("source"),
                        domain=item.get("domain"),
                        sentiment_label=sentiment.get("label", "neutral"),
                        sentiment_score=float(sentiment.get("sentiment_score", 0.0)),
                        sentiment_confidence=float(sentiment.get("confidence", 0.0)),
                    )
                )
            news_payload.append(SymbolNews(symbol=symbol, items=items_payload))

        return NewsResponse(
            success=True,
            symbols=symbol_list,
            data=news_payload,
            source="CryptoPanic",
            last_updated=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error fetching news: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


# Hybrid signal generation endpoint (stores in memory, publishes to Solana)
@app.post("/hybrid", response_model=HybridResponse)
async def generate_hybrid_signal(request: HybridRequest):
    if engine is None:
        raise HTTPException(status_code=503, detail="ML service not initialized")
    
    try:
        logger.info(f"Generating hybrid signal for {request.symbol}")
        
        # Get technical indicators directly
        technical_score = 0.0
        if indicators:
            try:
                technical_result = indicators.analyze(request.symbol, period="7d")
                if "error" not in technical_result:
                    technical_score = technical_result.get('technical_score', 0.0)
            except Exception as e:
                logger.warning(f"Error getting technical indicators: {e}")
        
        # For sentiment, we'll use a neutral score (you can enhance this by fetching news)
        # In a full implementation, you'd fetch crypto news and analyze it
        sentiment_score = 0.0
        
        # Calculate volatility (simplified - set to 0 for now)
        # You can enhance this by fetching price data and calculating variance
        volatility_index = 0.0
        
        # Compute hybrid score
        hybrid_score = engine.compute_hybrid_score(
            sentiment_score, 
            technical_score, 
            volatility_index
        )
        
        # Generate signal
        signal, reason = engine.generate_signal(hybrid_score)
        confidence = engine.compute_confidence(sentiment_score, technical_score, volatility_index)
        
        # Build reason with actual values
        reason = f"Technical Score: {technical_score:.3f}, Sentiment: {sentiment_score:.3f}, Volatility: {volatility_index:.3f}. {reason}"
        
        # Try to publish to Solana
        proof_hash = None
        tx_signature = None
        try:
            solana_result = send_proof({
                "symbol": request.symbol,
                "signal": signal,
                "hybrid_score": hybrid_score,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat()
            })
            proof_hash = solana_result.get("proof_hash")
            tx_signature = solana_result.get("tx_signature")
            logger.info(f"Published signal to Solana: {tx_signature}")
        except Exception as solana_error:
            logger.warning(f"Could not publish to Solana: {solana_error}")
        
        # Store in memory cache
        signal_data = {
            "id": len(signals_cache) + 1,
            "symbol": request.symbol,
            "signal": signal,
            "hybrid_score": hybrid_score,
            "confidence": confidence,
            "sentiment_score": sentiment_score,
            "technical_score": technical_score,
            "volatility_index": volatility_index,
            "reason": reason,
            "proof_hash": proof_hash,
            "tx_signature": tx_signature,
            "timestamp": datetime.now().isoformat()
        }
        signals_cache.append(signal_data)
        
        # Keep only last 100 signals in memory
        if len(signals_cache) > 100:
            signals_cache.pop(0)
        
        return HybridResponse(
            symbol=request.symbol,
            sentiment_score=sentiment_score if sentiment_score != 0.0 else None,
            technical_score=technical_score if technical_score != 0.0 else None,
            volatility_index=volatility_index if volatility_index != 0.0 else None,
            hybrid_score=hybrid_score,
            signal=signal,
            confidence=confidence,
            reason=reason,
            proof_hash=proof_hash,
            tx_signature=tx_signature
        )
        
    except Exception as e:
        logger.error(f"Error generating hybrid signal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get signals list from memory cache
@app.get("/signals/list")
async def get_signals_list(limit: int = 50, offset: int = 0):
    """
    Get list of signals from in-memory cache (no database)
    """
    try:
        # Reverse to show newest first
        signals = list(reversed(signals_cache))[offset:offset+limit]
        
        return {
            "success": True,
            "signals": signals,
            "count": len(signals),
            "total": len(signals_cache),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error fetching signals list: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main_no_db:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

