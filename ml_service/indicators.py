"""
Technical Indicators Module using pandas-ta and yfinance

This module downloads OHLC market data using yfinance and computes technical indicators:
- EMA20, EMA50: Exponential Moving Averages for trend identification
- RSI(14): Relative Strength Index for momentum (range 0-100)
- MACD(12,26,9): Moving Average Convergence Divergence for trend confirmation

Technical Score Calculation (normalized to -1.0 to +1.0):
- EMA trend: EMA20 > EMA50 = +0.4 (bullish), else -0.4 (bearish)
- RSI: <30 = +0.5 (oversold/bullish), >70 = -0.5 (overbought/bearish), else normalized
- MACD: MACD > Signal = +0.3 (bullish), else -0.3 (bearish)
- Final score = weighted sum of all components (range: -1.0 to +1.0)

The module integrates with PostgreSQL for persistent storage of indicator results.
"""

import logging
import os
from typing import Dict, Optional, Tuple
import numpy as np
import pandas as pd
try:
    import pandas_ta as ta
    HAS_PANDAS_TA = True
except ImportError:
    HAS_PANDAS_TA = False
    logging.warning("pandas_ta not available. Technical indicators will use manual calculations.")
import yfinance as yf
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, timedelta
from functools import lru_cache
from .crypto_data import get_crypto_data_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """
    Calculate technical indicators for trading signals
    
    Downloads market data using yfinance and computes EMA, RSI, MACD indicators.
    Calculates a composite technical score in range -1.0 to +1.0.
    """
    
    def __init__(self):
        """Initialize technical indicators calculator"""
        self.logger = logging.getLogger(__name__)
        self.cache = {}  # Simple in-memory cache
    
    def fetch_market_data(self, symbol: str, period: str = "3mo") -> Optional[pd.DataFrame]:
        """
        Fetch market data using crypto data service or yfinance as fallback
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT", "ETHUSDT", "AAPL")
            period: Time period for data (e.g., "1d", "5d", "1mo", "3mo", "1y")
            
        Returns:
            DataFrame with OHLCV data or None if error
        """
        try:
            logger.info(f"Fetching market data for {symbol} (period: {period})")
            
            # Check if it's a crypto symbol (ends with USDT, BTC, ETH, etc.)
            crypto_symbols = ["USDT", "BTC", "ETH", "SOL", "XRP", "ADA", "DOT", "LINK"]
            is_crypto = any(symbol.upper().endswith(suffix) for suffix in crypto_symbols)
            
            if is_crypto:
                # Use crypto data service
                crypto_manager = get_crypto_data_manager()
                df = crypto_manager.get_crypto_market_data(symbol, period)
            else:
                # Fallback to yfinance for traditional assets
                ticker = yf.Ticker(symbol)
                df = ticker.history(period=period)
                # Rename columns to lowercase for consistency
                if not df.empty:
                    df.columns = df.columns.str.lower()
            
            if df is None or df.empty:
                logger.error(f"No data available for symbol {symbol}")
                return None
            
            # Ensure required columns exist
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required_columns):
                logger.error(f"Missing required columns in data for {symbol}")
                return None
            
            logger.info(f"Fetched {len(df)} data points for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {e}")
            return None
    
    def calculate_ema(self, df: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        Calculate Exponential Moving Average
        
        Args:
            df: DataFrame with 'close' prices
            period: EMA period (default: 20)
            
        Returns:
            Series with EMA values
        """
        if HAS_PANDAS_TA:
            return ta.ema(df['close'], length=period)
        else:
            # Manual EMA calculation
            return df['close'].ewm(span=period, adjust=False).mean()
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index
        
        Args:
            df: DataFrame with 'close' prices
            period: RSI period (default: 14)
            
        Returns:
            Series with RSI values (0-100)
        """
        if HAS_PANDAS_TA:
            return ta.rsi(df['close'], length=period)
        else:
            # Manual RSI calculation
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
    
    def calculate_macd(self, df: pd.DataFrame, 
                       fast: int = 12, 
                       slow: int = 26, 
                       signal: int = 9) -> Dict[str, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            df: DataFrame with 'close' prices
            fast: Fast EMA period (default: 12)
            slow: Slow EMA period (default: 26)
            signal: Signal line period (default: 9)
            
        Returns:
            Dict with 'macd' line, 'signal' line, and 'histogram'
        """
        if HAS_PANDAS_TA:
            macd_data = ta.macd(df['close'], fast=fast, slow=slow, signal=signal)
            
            # Extract column names dynamically
            macd_col = f'MACD_{fast}_{slow}_{signal}'
            signal_col = f'MACDs_{fast}_{slow}_{signal}'
            hist_col = f'MACDh_{fast}_{slow}_{signal}'
            
            return {
                'macd': macd_data[macd_col] if macd_col in macd_data.columns else None,
                'signal': macd_data[signal_col] if signal_col in macd_data.columns else None,
                'histogram': macd_data[hist_col] if hist_col in macd_data.columns else None
            }
        else:
            # Manual MACD calculation
            ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
            ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal, adjust=False).mean()
            histogram = macd_line - signal_line
            
            return {
                'macd': macd_line,
                'signal': signal_line,
                'histogram': histogram
            }
    
    def calculate_technical_score(self, 
                                  ema20: float, 
                                  ema50: float,
                                  rsi: float, 
                                  macd_line: float,
                                  macd_signal: float = None) -> float:
        """
        Calculate composite technical score in range -1.0 to +1.0
        
        Args:
            ema20: EMA 20 value
            ema50: EMA 50 value
            rsi: RSI value (0-100)
            macd_line: MACD line value
            macd_signal: MACD signal line value (optional)
            
        Returns:
            Technical score between -1.0 and +1.0
            Negative = bearish, Positive = bullish, 0 = neutral
        """
        try:
            scores = []
            
            # 1. EMA trend signal (-0.4 to +0.4)
            if not pd.isna(ema20) and not pd.isna(ema50) and ema50 > 0:
                if ema20 > ema50:
                    ema_score = 0.4  # Bullish trend
                else:
                    ema_score = -0.4  # Bearish trend
                scores.append(ema_score)
            
            # 2. RSI signal (-0.5 to +0.5)
            if not pd.isna(rsi):
                if rsi > 70:
                    rsi_score = -0.5  # Overbought = bearish
                elif rsi < 30:
                    rsi_score = 0.5  # Oversold = bullish
                else:
                    # Linear mapping: 30 -> 0.5, 50 -> 0, 70 -> -0.5
                    rsi_score = 0.5 - ((rsi - 30) / 40) * 1.0
                scores.append(rsi_score)
            
            # 3. MACD signal (-0.3 to +0.3)
            if macd_signal is not None and not pd.isna(macd_line) and not pd.isna(macd_signal):
                if macd_line > macd_signal:
                    macd_score = 0.3  # Bullish crossover
                else:
                    macd_score = -0.3  # Bearish crossover
                scores.append(macd_score)
            elif not pd.isna(macd_line):
                # If no signal line, use normalized MACD value
                macd_score = np.tanh(macd_line / 10) * 0.3  # Normalize to -0.3 to +0.3
                scores.append(macd_score)
            
            # Calculate weighted sum
            if scores:
                technical_score = np.sum(scores)
                # Clamp to -1.0 to +1.0 range
                technical_score = max(-1.0, min(1.0, technical_score))
                return round(float(technical_score), 4)
            else:
                return 0.0  # Neutral if no indicators available
                
        except Exception as e:
            logger.error(f"Error calculating technical score: {e}")
            return 0.0
    
    def analyze(self, symbol: str, period: str = "3mo") -> Dict:
        """
        Perform complete technical analysis for a symbol
        
        Args:
            symbol: Trading symbol to analyze
            period: Time period for data (default: "3mo")
            
        Returns:
            Dict with all technical indicators and composite score
        """
        try:
            # Check cache first
            cache_key = f"{symbol}_{period}"
            if cache_key in self.cache:
                cache_time, cached_data = self.cache[cache_key]
                # Use cache if less than 15 minutes old
                if datetime.now() - cache_time < timedelta(minutes=15):
                    logger.info(f"Using cached data for {symbol}")
                    return cached_data
            
            # Fetch market data
            df = self.fetch_market_data(symbol, period)
            if df is None or df.empty:
                return {
                    "symbol": symbol,
                    "ema20": None,
                    "ema50": None,
                    "rsi": None,
                    "macd": None,
                    "technical_score": 0.0,
                    "error": "Failed to fetch market data"
                }
            
            # Calculate indicators
            ema20 = self.calculate_ema(df, period=20)
            ema50 = self.calculate_ema(df, period=50)
            rsi = self.calculate_rsi(df, period=14)
            macd_data = self.calculate_macd(df)
            
            # Get latest values
            latest_idx = -1
            ema20_val = ema20.iloc[latest_idx] if len(ema20) > 0 else None
            ema50_val = ema50.iloc[latest_idx] if len(ema50) > 0 else None
            rsi_val = rsi.iloc[latest_idx] if len(rsi) > 0 else None
            macd_val = macd_data['macd'].iloc[latest_idx] if macd_data['macd'] is not None and len(macd_data['macd']) > 0 else None
            macd_signal_val = macd_data['signal'].iloc[latest_idx] if macd_data['signal'] is not None and len(macd_data['signal']) > 0 else None
            
            # Handle NaN values
            ema20_val = None if pd.isna(ema20_val) else ema20_val
            ema50_val = None if pd.isna(ema50_val) else ema50_val
            rsi_val = None if pd.isna(rsi_val) else rsi_val
            macd_val = None if pd.isna(macd_val) else macd_val
            macd_signal_val = None if pd.isna(macd_signal_val) else macd_signal_val
            
            # Calculate technical score
            technical_score = self.calculate_technical_score(
                ema20_val, ema50_val, rsi_val, macd_val, macd_signal_val
            )
            
            result = {
                "symbol": symbol,
                "ema20": float(ema20_val) if ema20_val is not None else None,
                "ema50": float(ema50_val) if ema50_val is not None else None,
                "rsi": float(rsi_val) if rsi_val is not None else None,
                "macd": float(macd_val) if macd_val is not None else None,
                "technical_score": technical_score
            }
            
            # Update cache
            self.cache[cache_key] = (datetime.now(), result)
            
            logger.info(f"Technical analysis complete for {symbol}: score={technical_score:.4f}")
            return result
            
        except Exception as e:
            logger.error(f"Error in technical analysis for {symbol}: {e}")
            return {
                "symbol": symbol,
                "ema20": None,
                "ema50": None,
                "rsi": None,
                "macd": None,
                "technical_score": 0.0,
                "error": str(e)
            }


class TechnicalDBManager:
    """
    Manages PostgreSQL connection and operations for technical indicators
    """
    
    def __init__(self, 
                 host: str = "postgres",
                 user: str = "postgres",
                 password: str = "postgres",
                 dbname: str = "sentiment_market",
                 port: int = 5432):
        """
        Initialize database connection
        
        Args:
            host: Database host
            user: Database user
            password: Database password
            dbname: Database name
            port: Database port
        """
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
            logger.info("Connected to PostgreSQL database (Technical Indicators)")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def save_technical_indicators(self, symbol: str, ema20: float, ema50: float,
                                  rsi: float, macd: float, technical_score: float) -> int:
        """
        Save technical indicators to database
        
        Args:
            symbol: Trading symbol
            ema20: EMA 20 value
            ema50: EMA 50 value
            rsi: RSI value
            macd: MACD value
            technical_score: Technical score (-1.0 to +1.0)
            
        Returns:
            Inserted record ID
        """
        try:
            cur = self.conn.cursor()
            cur.execute(
                """
                INSERT INTO technical_indicators 
                (symbol, ema20, ema50, rsi, macd, technical_score, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                RETURNING id
                """,
                (symbol, ema20, ema50, rsi, macd, technical_score)
            )
            result = cur.fetchone()
            self.conn.commit()
            cur.close()
            
            record_id = result[0] if result else None
            logger.debug(f"Saved technical indicators for {symbol} with ID: {record_id}")
            return record_id
            
        except Exception as e:
            logger.error(f"Error saving technical indicators: {e}")
            self.conn.rollback()
            return None
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed (Technical Indicators)")


# Global instances
_indicators: Optional[TechnicalIndicators] = None
_db_manager: Optional[TechnicalDBManager] = None


def get_indicators() -> TechnicalIndicators:
    """Get or create the global technical indicators instance"""
    global _indicators
    if _indicators is None:
        _indicators = TechnicalIndicators()
    return _indicators


def get_db_manager() -> Optional[TechnicalDBManager]:
    """Get or create the global database manager instance"""
    global _db_manager
    if _db_manager is None:
        try:
            _db_manager = TechnicalDBManager(
                host=os.getenv("DB_HOST", "postgres"),
                user=os.getenv("POSTGRES_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD", "postgres"),
                dbname=os.getenv("POSTGRES_DB", "sentiment_market"),
                port=int(os.getenv("POSTGRES_PORT", "5432"))
            )
        except Exception as e:
            logger.warning(f"Could not initialize database manager: {e}")
            logger.warning("Running without database persistence")
    return _db_manager


if __name__ == "__main__":
    """
    Example usage and testing
    Run with: python ml_service/indicators.py
    """
    import sys
    from pathlib import Path
    
    # Add parent directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent))
    
    print("\n" + "="*70)
    print("Technical Indicators Module Test")
    print("="*70)
    
    # Initialize indicators
    indicators = get_indicators()
    
    # Test symbols
    test_symbols = ["AAPL", "BTC-USD", "ETH-USD", "TSLA"]
    
    print("\nAnalyzing symbols...")
    print("-"*70)
    
    for symbol in test_symbols:
        print(f"\nAnalyzing {symbol}...")
        result = indicators.analyze(symbol, period="3mo")
        
        if "error" not in result:
            print(f"  EMA 20: {result['ema20']:.2f if result['ema20'] else 'N/A'}")
            print(f"  EMA 50: {result['ema50']:.2f if result['ema50'] else 'N/A'}")
            print(f"  RSI: {result['rsi']:.2f if result['rsi'] else 'N/A'}")
            print(f"  MACD: {result['macd']:.4f if result['macd'] else 'N/A'}")
            print(f"  Technical Score: {result['technical_score']:.4f}")
        else:
            print(f"  Error: {result['error']}")
    
    # Database test (if available)
    try:
        db = get_db_manager()
        if db:
            print("\n" + "="*70)
            print("Database Integration Test")
            print("="*70)
            
            test_result = indicators.analyze("AAPL", period="3mo")
            if "error" not in test_result and test_result['ema20'] is not None:
                record_id = db.save_technical_indicators(
                    symbol=test_result['symbol'],
                    ema20=test_result['ema20'],
                    ema50=test_result['ema50'],
                    rsi=test_result['rsi'],
                    macd=test_result['macd'],
                    technical_score=test_result['technical_score']
                )
                print(f"Saved test result with ID: {record_id}")
            db.close()
    except Exception as e:
        print(f"Database test failed: {e}")
    
    print("\n" + "="*70)
    print("Test Complete")
    print("="*70)
