"""
Crypto-Focused Hybrid AI Decision Engine
Combines sentiment analysis, technical indicators, and volatility to generate intelligent crypto trading signals

This module implements a hybrid decision system that merges sentiment, technical, and volatility signals
using adaptive weighting. The hybrid score is calculated as:

hybrid_score = α * sentiment_score + β * technical_score + γ * volatility_index

where α (sentiment weight) defaults to 0.5, β (technical weight) defaults to 0.3, and γ (volatility weight) defaults to 0.2.

Signal Generation Logic:
- hybrid_score > 0.3  → BUY signal (bullish momentum)
- hybrid_score < -0.3 → SELL signal (bearish momentum)
- -0.3 ≤ hybrid_score ≤ 0.3 → HOLD signal (neutral)

Confidence Calculation:
confidence = (abs(sentiment_score) * α + abs(technical_score) * β + abs(volatility_index) * γ)

The module fetches the latest sentiment, technical, and volatility data from PostgreSQL tables
and generates comprehensive crypto trading signals with human-readable reasoning.
"""

import logging
import os
import numpy as np
from typing import Dict, Optional, Tuple
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Signal(Enum):
    """Trading signal types"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class HybridEngine:
    """
    Crypto-focused Hybrid AI Decision Engine combining sentiment, technical analysis, and volatility
    
    Fetches latest sentiment, technical, and volatility data from PostgreSQL, computes
    weighted hybrid score, and generates actionable crypto trading signals.
    """
    
    def __init__(self, sentiment_weight: float = 0.5, technical_weight: float = 0.3, volatility_weight: float = 0.2):
        """
        Initialize hybrid decision engine
        
        Args:
            sentiment_weight: Weight α for sentiment analysis (default: 0.5)
            technical_weight: Weight β for technical indicators (default: 0.3)
            volatility_weight: Weight γ for volatility analysis (default: 0.2)
        """
        self.alpha = sentiment_weight
        self.beta = technical_weight
        self.gamma = volatility_weight
        
        # Normalize weights to sum to 1
        total_weight = sentiment_weight + technical_weight + volatility_weight
        if total_weight > 0:
            self.alpha = sentiment_weight / total_weight
            self.beta = technical_weight / total_weight
            self.gamma = volatility_weight / total_weight
        else:
            self.alpha = 0.5
            self.beta = 0.3
            self.gamma = 0.2
        
        logger.info(f"Hybrid Engine initialized with weights - "
                   f"α (sentiment): {self.alpha:.2f}, "
                   f"β (technical): {self.beta:.2f}, "
                   f"γ (volatility): {self.gamma:.2f}")
    
    def fetch_sentiment_data(self, symbol: str, db_conn) -> Optional[Dict]:
        """
        Fetch latest sentiment data for a symbol from PostgreSQL
        
        Args:
            symbol: Trading symbol to fetch data for
            db_conn: PostgreSQL connection object
            
        Returns:
            Dict with sentiment data or None if not found
        """
        try:
            cur = db_conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(
                """
                SELECT symbol, sentiment_score, label, confidence, timestamp
                FROM sentiment_results
                WHERE symbol = %s
                ORDER BY timestamp DESC
                LIMIT 1
                """,
                (symbol,)
            )
            result = cur.fetchone()
            cur.close()
            
            if result:
                logger.debug(f"Fetched sentiment data for {symbol}")
                return dict(result)
            else:
                logger.warning(f"No sentiment data found for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching sentiment data for {symbol}: {e}")
            return None
    
    def fetch_technical_data(self, symbol: str, db_conn) -> Optional[Dict]:
        """
        Fetch latest technical data for a symbol from PostgreSQL
        
        Args:
            symbol: Trading symbol to fetch data for
            db_conn: PostgreSQL connection object
            
        Returns:
            Dict with technical data or None if not found
        """
        try:
            cur = db_conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(
                """
                SELECT symbol, ema20, ema50, rsi, macd, technical_score, timestamp
                FROM technical_indicators
                WHERE symbol = %s
                ORDER BY timestamp DESC
                LIMIT 1
                """,
                (symbol,)
            )
            result = cur.fetchone()
            cur.close()
            
            if result:
                logger.debug(f"Fetched technical data for {symbol}")
                return dict(result)
            else:
                logger.warning(f"No technical data found for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching technical data for {symbol}: {e}")
            return None
    
    def calculate_volatility_index(self, symbol: str, db_conn, period_days: int = 7) -> Optional[float]:
        """
        Calculate volatility index based on price variance
        
        Args:
            symbol: Trading symbol
            db_conn: Database connection
            period_days: Number of days to look back for volatility calculation
            
        Returns:
            Volatility index (-1.0 to +1.0) or None if error
        """
        try:
            cur = db_conn.cursor()
            
            # Fetch recent price data
            query = """
            SELECT close, timestamp 
            FROM market_data 
            WHERE symbol = %s 
            AND timestamp >= NOW() - INTERVAL '%s days'
            ORDER BY timestamp DESC
            LIMIT 100
            """
            
            cur.execute(query, (symbol, period_days))
            rows = cur.fetchall()
            
            if len(rows) < 10:  # Need minimum data points
                logger.warning(f"Insufficient data for volatility calculation: {len(rows)} points")
                return None
            
            # Extract close prices
            prices = [float(row[0]) for row in rows]
            
            # Calculate price changes (returns)
            returns = []
            for i in range(1, len(prices)):
                if prices[i-1] != 0:
                    returns.append((prices[i] - prices[i-1]) / prices[i-1])
            
            if not returns:
                return None
            
            # Calculate volatility (standard deviation of returns)
            volatility = np.std(returns)
            
            # Normalize volatility to -1.0 to +1.0 range
            # High volatility (>0.05) = +1.0, Low volatility (<0.01) = -1.0
            if volatility > 0.05:
                volatility_index = 1.0
            elif volatility < 0.01:
                volatility_index = -1.0
            else:
                # Linear interpolation between -1.0 and +1.0
                volatility_index = (volatility - 0.01) / (0.05 - 0.01) * 2.0 - 1.0
            
            logger.info(f"Volatility index for {symbol}: {volatility_index:.4f} (raw volatility: {volatility:.4f})")
            return volatility_index
            
        except Exception as e:
            logger.error(f"Error calculating volatility index: {e}")
            return None
    
    def compute_hybrid_score(self, sentiment_score: float, 
                            technical_score: float, 
                            volatility_index: float = 0.0) -> float:
        """
        Compute hybrid score using weighted combination with volatility
        
        Formula: hybrid_score = α * sentiment_score + β * technical_score + γ * volatility_index
        
        Args:
            sentiment_score: Sentiment score (-1.0 to +1.0)
            technical_score: Technical score (-1.0 to +1.0)
            volatility_index: Volatility index (-1.0 to +1.0)
            
        Returns:
            Hybrid score in range -1.0 to +1.0
        """
        try:
            hybrid_score = (self.alpha * sentiment_score) + (self.beta * technical_score) + (self.gamma * volatility_index)
            return round(hybrid_score, 4)
        except Exception as e:
            logger.error(f"Error computing hybrid score: {e}")
            return 0.0
    
    def compute_confidence(self, sentiment_score: float, 
                          technical_score: float,
                          volatility_index: float = 0.0) -> float:
        """
        Compute confidence based on weighted absolute values including volatility
        
        Formula: confidence = (abs(sentiment_score) * α + abs(technical_score) * β + abs(volatility_index) * γ)
        
        Args:
            sentiment_score: Sentiment score
            technical_score: Technical score
            volatility_index: Volatility index
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        try:
            confidence = (abs(sentiment_score) * self.alpha) + (abs(technical_score) * self.beta) + (abs(volatility_index) * self.gamma)
            # Clamp to 0-1 range
            confidence = max(0.0, min(1.0, confidence))
            return round(confidence, 4)
        except Exception as e:
            logger.error(f"Error computing confidence: {e}")
            return 0.5
    
    def generate_signal(self, hybrid_score: float) -> Tuple[str, str]:
        """
        Generate trading signal based on hybrid score thresholds
        
        Args:
            hybrid_score: Hybrid score (-1.0 to +1.0)
            
        Returns:
            Tuple of (signal, reason)
        """
        try:
            if hybrid_score > 0.3:
                signal = "BUY"
                reason = self._generate_buy_reason(hybrid_score)
            elif hybrid_score < -0.3:
                signal = "SELL"
                reason = self._generate_sell_reason(hybrid_score)
            else:
                signal = "HOLD"
                reason = self._generate_hold_reason(hybrid_score)
            
            return signal, reason
            
        except Exception as e:
            logger.error(f"Error generating signal: {e}")
            return "HOLD", "Error in signal generation"
    
    def _generate_buy_reason(self, hybrid_score: float) -> str:
        """Generate reason for BUY signal"""
        if hybrid_score > 0.7:
            return "Strong bullish momentum with very positive sentiment and technical indicators"
        elif hybrid_score > 0.5:
            return "Positive sentiment and bullish technical indicators suggesting upward trend"
        else:
            return "Moderate positive sentiment with favorable technical setup"
    
    def _generate_sell_reason(self, hybrid_score: float) -> str:
        """Generate reason for SELL signal"""
        if hybrid_score < -0.7:
            return "Strong bearish momentum with negative sentiment and weak technical indicators"
        elif hybrid_score < -0.5:
            return "Negative sentiment and bearish technical indicators suggesting downward trend"
        else:
            return "Moderate negative sentiment with unfavorable technical setup"
    
    def _generate_hold_reason(self, hybrid_score: float) -> str:
        """Generate reason for HOLD signal"""
        if abs(hybrid_score) < 0.1:
            return "Neutral sentiment and technical indicators showing balanced market conditions"
        else:
            return "Mixed signals with sentiment and technical indicators showing conflicting trends"
    
    def analyze_symbol(self, symbol: str, db_conn) -> Dict:
        """
        Complete hybrid analysis for a symbol
        
        Fetches sentiment and technical data, computes hybrid score,
        generates signal, and returns comprehensive result.
        
        Args:
            symbol: Trading symbol to analyze
            db_conn: PostgreSQL connection object
            
        Returns:
            Dict with complete analysis results
        """
        try:
            # Fetch latest data
            sentiment_data = self.fetch_sentiment_data(symbol, db_conn)
            technical_data = self.fetch_technical_data(symbol, db_conn)
            volatility_index = self.calculate_volatility_index(symbol, db_conn)
            
            # Check if we have sufficient data
            if sentiment_data is None and technical_data is None:
                return {
                    "symbol": symbol,
                    "error": "No sentiment or technical data available",
                    "sentiment_score": None,
                    "technical_score": None,
                    "volatility_index": volatility_index or 0.0,
                    "hybrid_score": 0.0,
                    "signal": "HOLD",
                    "confidence": 0.0,
                    "reason": "Insufficient data for analysis"
                }
            
            # Extract scores (handle missing data)
            sentiment_score = sentiment_data.get('sentiment_score', 0.0) if sentiment_data else 0.0
            technical_score = technical_data.get('technical_score', 0.0) if technical_data else 0.0
            volatility_index = volatility_index or 0.0
            
            # If only one data source, use it with reduced confidence
            if sentiment_data is None:
                hybrid_score = technical_score
                confidence = 0.5  # Reduced confidence
                reason_base = "Technical analysis only"
            elif technical_data is None:
                hybrid_score = sentiment_score
                confidence = 0.5  # Reduced confidence
                reason_base = "Sentiment analysis only"
            else:
                # Compute hybrid score using all sources
                hybrid_score = self.compute_hybrid_score(sentiment_score, technical_score, volatility_index)
                confidence = self.compute_confidence(sentiment_score, technical_score, volatility_index)
                reason_base = f"Sentiment: {sentiment_score:.2f}, Technical: {technical_score:.2f}, Volatility: {volatility_index:.2f}"
            
            # Generate signal
            signal, reason = self.generate_signal(hybrid_score)
            
            # Combine reason base with signal-specific reason
            full_reason = f"{reason_base}. {reason}"
            
            return {
                "symbol": symbol,
                "sentiment_score": sentiment_score if sentiment_data else None,
                "technical_score": technical_score if technical_data else None,
                "hybrid_score": hybrid_score,
                "signal": signal,
                "confidence": confidence,
                "reason": full_reason
            }
            
        except Exception as e:
            logger.error(f"Error analyzing symbol {symbol}: {e}")
            return {
                "symbol": symbol,
                "error": str(e),
                "sentiment_score": None,
                "technical_score": None,
                "hybrid_score": 0.0,
                "signal": "HOLD",
                "confidence": 0.0,
                "reason": "Error in analysis"
            }


class HybridDBManager:
    """
    Manages PostgreSQL operations for hybrid signals
    """
    
    def __init__(self, 
                 host: str = "postgres",
                 user: str = "postgres",
                 password: str = "postgres",
                 dbname: str = "sentiment_market",
                 port: int = 5432):
        """Initialize database connection"""
        self.connection_string = {
            "host": host,
            "user": user,
            "password": password,
            "dbname": dbname,
            "port": port
        }
        self.conn = None
        self._connect()
    
    def _connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.connection_string)
            logger.info("Connected to PostgreSQL database (Hybrid Signals)")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def save_hybrid_signal(self, symbol: str, sentiment_score: float,
                           technical_score: float, hybrid_score: float,
                           signal: str, reason: str, confidence: float) -> int:
        """
        Save hybrid signal to database
        
        Args:
            symbol: Trading symbol
            sentiment_score: Sentiment score
            technical_score: Technical score
            hybrid_score: Hybrid score
            signal: Trading signal (BUY/SELL/HOLD)
            reason: Signal reasoning
            confidence: Confidence score
            
        Returns:
            Inserted record ID
        """
        try:
            cur = self.conn.cursor()
            cur.execute(
                """
                INSERT INTO hybrid_signals 
                (symbol, sentiment_score, technical_score, hybrid_score, signal, reason, confidence, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                RETURNING id
                """,
                (symbol, sentiment_score, technical_score, hybrid_score, signal, reason, confidence)
            )
            result = cur.fetchone()
            self.conn.commit()
            cur.close()
            
            record_id = result[0] if result else None
            logger.debug(f"Saved hybrid signal for {symbol} with ID: {record_id}")
            return record_id
            
        except Exception as e:
            logger.error(f"Error saving hybrid signal: {e}")
            self.conn.rollback()
            return None
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed (Hybrid Signals)")


# Global instances
_engine: Optional[HybridEngine] = None
_db_manager: Optional[HybridDBManager] = None


def get_engine(sentiment_weight: float = 0.6, technical_weight: float = 0.4) -> HybridEngine:
    """Get or create the global hybrid engine instance"""
    global _engine
    if _engine is None:
        _engine = HybridEngine(sentiment_weight, technical_weight)
    return _engine


def get_db_manager() -> Optional[HybridDBManager]:
    """Get or create the global database manager instance"""
    global _db_manager
    if _db_manager is None:
        try:
            _db_manager = HybridDBManager(
                host=os.getenv("DB_HOST", "postgres"),
                user=os.getenv("POSTGRES_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD", "postgres"),
                dbname=os.getenv("POSTGRES_DB", "sentiment_market"),
                port=int(os.getenv("POSTGRES_PORT", "5432"))
            )
        except Exception as e:
            logger.warning(f"Could not initialize hybrid database manager: {e}")
            logger.warning("Running without database persistence")
    return _db_manager


if __name__ == "__main__":
    """
    Example usage and testing
    Run with: python ml_service/hybrid_engine.py
    """
    import sys
    from pathlib import Path
    
    sys.path.insert(0, str(Path(__file__).parent))
    
    print("\n" + "="*70)
    print("Hybrid AI Decision Engine Test")
    print("="*70)
    
    # Initialize engine
    engine = get_engine(sentiment_weight=0.6, technical_weight=0.4)
    db = get_db_manager()
    
    if not db:
        print("❌ Database connection failed. Please ensure PostgreSQL is running.")
        sys.exit(1)
    
    # Test symbols
    test_symbols = ["AAPL", "BTC-USD", "ETH-USD"]
    
    print("\nAnalyzing symbols...")
    print("-"*70)
    
    for symbol in test_symbols:
        print(f"\nSymbol: {symbol}")
        result = engine.analyze_symbol(symbol, db.conn)
        
        if "error" not in result:
            print(f"  Sentiment Score: {result['sentiment_score']:.4f if result['sentiment_score'] is not None else 'N/A'}")
            print(f"  Technical Score: {result['technical_score']:.4f if result['technical_score'] is not None else 'N/A'}")
            print(f"  Hybrid Score: {result['hybrid_score']:.4f}")
            print(f"  Signal: {result['signal']}")
            print(f"  Confidence: {result['confidence']:.4f}")
            print(f"  Reason: {result['reason']}")
        else:
            print(f"  Error: {result['error']}")
    
    db.close()
    
    print("\n" + "="*70)
    print("Test Complete")
    print("="*70)
