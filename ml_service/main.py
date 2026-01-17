"""
FastAPI Main Application for ML Service (No Database Version)
Simplified version that works without PostgreSQL
"""

import logging
import os
import random
from typing import List, Optional
from datetime import datetime
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ml_service.sentiment import get_analyzer
from ml_service.indicators import get_indicators
from ml_service.hybrid_engine import get_db_manager, get_engine
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

# Global managers/components (initialized lazily at startup)
analyzer = None
indicators = None
engine = None
news_manager = None
db_manager = None
_init_error: Optional[str] = None
_init_task: Optional[asyncio.Task] = None

# Solana publish policy (to avoid spamming devnet)
_solana_published_count = 0

# Initialize FastAPI app
app = FastAPI(
    title="AI Sentiment Market Prediction - ML Service (No DB)",
    description="Machine Learning service for sentiment analysis and technical indicators (No database required)",
    version="1.0.0"
)


def _init_components_sync() -> None:
    global analyzer, indicators, engine, news_manager, db_manager, _init_error
    try:
        analyzer = get_analyzer()
        indicators = get_indicators()
        engine = get_engine(sentiment_weight=0.5, technical_weight=0.3)
        news_manager = get_crypto_news_manager(analyzer)
        # Optional database manager (enabled only if psycopg2 is installed and connection works)
        db_manager = get_db_manager()
        _init_error = None
        logger.info("All ML components initialized successfully (No database mode)")
    except Exception as e:
        _init_error = str(e)
        analyzer = None
        indicators = None
        engine = None
        news_manager = None
        db_manager = None
        logger.error(f"Error initializing ML components: {e}")


async def _init_components_async() -> None:
    await asyncio.to_thread(_init_components_sync)


def _service_ready() -> bool:
    return analyzer is not None and indicators is not None and engine is not None


def _parse_float_env(name: str, default_value: float) -> float:
    raw = os.getenv(name, "")
    if raw == "":
        return default_value
    try:
        return float(raw)
    except ValueError:
        return default_value


def _parse_int_env(name: str, default_value: int) -> int:
    raw = os.getenv(name, "")
    if raw == "":
        return default_value
    try:
        return int(raw)
    except ValueError:
        return default_value


def _should_publish_to_solana() -> bool:
    """Return True if we should attempt Solana anchoring for this signal."""
    global _solana_published_count

    enabled = os.getenv("SOLANA_PUBLISH_ENABLED", "false").lower() == "true"
    if not enabled:
        return False

    max_count = _parse_int_env("SOLANA_PUBLISH_MAX_COUNT", 5)
    if max_count >= 0 and _solana_published_count >= max_count:
        return False

    sample_rate = _parse_float_env("SOLANA_PUBLISH_SAMPLE_RATE", 0.1)
    # Clamp to [0,1]
    if sample_rate <= 0.0:
        return False
    if sample_rate >= 1.0:
        return True

    return random.random() < sample_rate


def _require_ready(feature: str) -> None:
    if _service_ready():
        return
    if _init_error:
        raise HTTPException(
            status_code=503,
            detail=f"{feature} unavailable: initialization failed: {_init_error}",
        )
    raise HTTPException(status_code=503, detail=f"{feature} unavailable: service warming up")


@app.on_event("startup")
async def startup_event():
    global _init_task
    # Start background initialization so uvicorn can bind the port immediately.
    if _init_task is None:
        _init_task = asyncio.create_task(_init_components_async())

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    preset: Optional[str] = Field(
        "balanced",
        description="Rule strictness preset: strict, balanced, or aggressive",
    )
    rules: Optional[dict] = Field(
        None,
        description="Optional rule toggles for demo/customization (e.g. enable_vwap=false). RSI is always enforced.",
    )


class InstitutionalProofRequest(BaseModel):
    signal: dict = Field(..., description="Institutional signal payload to anchor on-chain")

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
        models_loaded=_service_ready()
    )

# Sentiment analysis endpoint (no database saving)
@app.post("/sentiment", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest):
    _require_ready("sentiment")
    
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

        preset = (request.preset or "balanced").strip().lower()

        data_manager = get_crypto_data_manager()
        if request.use_sentiment:
            result, _debug = generate_institutional_signal_debug(
                symbol=request.symbol,
                data_manager=data_manager,
                news_manager=news_manager,
                timeframe=timeframe,
                use_sentiment=True,
                preset=preset,
                rules=request.rules,
            )
        else:
            result = generate_institutional_signal(
                symbol=request.symbol,
                data_manager=data_manager,
                news_manager=news_manager,
                timeframe=timeframe,
                preset=preset,
                rules=request.rules,
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

        preset = (request.preset or "balanced").strip().lower()

        data_manager = get_crypto_data_manager()
        result, debug = generate_institutional_signal_debug(
            symbol=request.symbol,
            data_manager=data_manager,
            news_manager=news_manager,
            timeframe=timeframe,
            use_sentiment=bool(request.use_sentiment),
            preset=preset,
            rules=request.rules,
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


@app.post("/signal/institutional/proof")
async def institutional_signal_proof(request: InstitutionalProofRequest):
    try:
        solana_result = send_proof(request.signal)
        return solana_result
    except Exception as e:
        logger.error(f"Error publishing institutional proof to Solana: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Technical indicators endpoint (no database saving)
@app.post("/technical", response_model=TechnicalResponse)
async def calculate_technical(request: TechnicalRequest):
    _require_ready("technical")
    
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
    _require_ready("news")

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
    _require_ready("hybrid")
    
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
        
        # Try to publish to Solana (controlled by env policy)
        proof_hash = None
        tx_signature = None
        if _should_publish_to_solana():
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
                global _solana_published_count
                _solana_published_count += 1
                logger.info(f"Published signal to Solana: {tx_signature}")
            except Exception as solana_error:
                logger.warning(f"Could not publish to Solana: {solana_error}")
        
        # Persist to database if available; otherwise store in memory cache
        record_id = None
        if db_manager is not None:
            try:
                record_id = db_manager.save_hybrid_signal(
                    symbol=request.symbol,
                    sentiment_score=sentiment_score,
                    technical_score=technical_score,
                    hybrid_score=hybrid_score,
                    signal=signal,
                    reason=reason,
                    confidence=confidence,
                    proof_hash=proof_hash,
                    tx_signature=tx_signature,
                )
            except Exception as db_error:
                logger.warning(f"Could not persist hybrid signal to database: {db_error}")

        # Store in memory cache (still useful for no-db mode, and as a fallback)
        signal_data = {
            "id": record_id if record_id is not None else (len(signals_cache) + 1),
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
    Get list of signals.
    If database persistence is available, returns newest signals from PostgreSQL.
    Otherwise, returns signals from the in-memory cache.
    """
    try:
        if db_manager is not None and getattr(db_manager, "conn", None) is not None:
            cur = db_manager.conn.cursor()
            cur.execute(
                """
                SELECT id, symbol, signal, hybrid_score, confidence, sentiment_score, technical_score,
                       volatility_index, reason, proof_hash, tx_signature, timestamp, created_at
                FROM hybrid_signals
                ORDER BY timestamp DESC
                LIMIT %s OFFSET %s
                """,
                (limit, offset),
            )
            rows = cur.fetchall()
            cur.close()

            signals = []
            for r in rows:
                signals.append(
                    {
                        "id": r[0],
                        "symbol": r[1],
                        "signal": r[2],
                        "hybrid_score": float(r[3]) if r[3] is not None else None,
                        "confidence": float(r[4]) if r[4] is not None else None,
                        "sentiment_score": float(r[5]) if r[5] is not None else None,
                        "technical_score": float(r[6]) if r[6] is not None else None,
                        "volatility_index": float(r[7]) if r[7] is not None else None,
                        "reason": r[8],
                        "proof_hash": r[9],
                        "tx_signature": r[10],
                        "timestamp": r[11].isoformat() if r[11] is not None else None,
                        "created_at": r[12].isoformat() if r[12] is not None else None,
                    }
                )

            return {
                "success": True,
                "signals": signals,
                "count": len(signals),
                "limit": limit,
                "offset": offset,
                "source": "postgres",
            }

        # Reverse to show newest first (cache)
        signals = list(reversed(signals_cache))[offset:offset+limit]

        return {
            "success": True,
            "signals": signals,
            "count": len(signals),
            "total": len(signals_cache),
            "limit": limit,
            "offset": offset,
            "source": "memory",
        }
    except Exception as e:
        logger.error(f"Error fetching signals list: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "ml_service.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
