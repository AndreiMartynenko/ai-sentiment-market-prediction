"""
Technical Indicators Module using pandas-ta
Calculates EMA, RSI, MACD and generates technical scores
"""

import logging
import numpy as np
import pandas as pd
import pandas_ta as ta
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TechnicalIndicators:
    """Calculate technical indicators for trading signals"""
    
    def __init__(self):
        """Initialize technical indicators calculator"""
        self.logger = logging.getLogger(__name__)
    
    def calculate_ema(self, df: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        Calculate Exponential Moving Average
        
        Args:
            df: DataFrame with 'close' prices
            period: EMA period (default: 20)
            
        Returns:
            Series with EMA values
        """
        return ta.ema(df['close'], length=period)
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index
        
        Args:
            df: DataFrame with 'close' prices
            period: RSI period (default: 14)
            
        Returns:
            Series with RSI values
        """
        return ta.rsi(df['close'], length=period)
    
    def calculate_macd(self, df: pd.DataFrame, 
                       fast: int = 12, 
                       slow: int = 26, 
                       signal: int = 9) -> Dict[str, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            df: DataFrame with 'close' prices
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
            
        Returns:
            Dict with MACD line, signal line, and histogram
        """
        macd_data = ta.macd(df['close'], fast=fast, slow=slow, signal=signal)
        return {
            'macd': macd_data[f'MACD_{fast}_{slow}_{signal}'],
            'signal': macd_data[f'MACDs_{fast}_{slow}_{signal}'],
            'histogram': macd_data[f'MACDh_{fast}_{slow}_{signal}']
        }
    
    def calculate_technical_score(self, 
                                  ema20: float, 
                                  ema50: float,
                                  rsi: float, 
                                  macd: float) -> float:
        """
        Calculate composite technical score based on multiple indicators
        
        Args:
            ema20: EMA 20 value
            ema50: EMA 50 value
            rsi: RSI value (0-100)
            macd: MACD line value
            
        Returns:
            Technical score between 0 and 1 (0=bearish, 1=bullish)
        """
        try:
            scores = []
            
            # EMA trend signal (0-1)
            if not pd.isna(ema20) and not pd.isna(ema50) and ema50 > 0:
                ema_signal = 1.0 if ema20 > ema50 else 0.0
                ema_strength = abs(ema20 - ema50) / ema50
                ema_score = ema_signal * min(ema_strength * 10, 1.0)
                scores.append(ema_score)
            
            # RSI signal (0-1)
            if not pd.isna(rsi):
                # RSI > 70: overbought, RSI < 30: oversold
                if rsi > 70:
                    rsi_score = 0.2  # Overbought - bearish
                elif rsi < 30:
                    rsi_score = 0.8  # Oversold - bullish
                else:
                    # Linear mapping: 30 -> 0.8, 70 -> 0.2
                    rsi_score = 0.8 - (rsi - 30) * 0.015
                scores.append(rsi_score)
            
            # MACD signal (0-1)
            if not pd.isna(macd):
                macd_score = 0.5 + np.tanh(macd) * 0.5
                scores.append(macd_score)
            
            # Calculate weighted average
            if scores:
                technical_score = np.mean(scores)
                return round(float(technical_score), 4)
            else:
                return 0.5  # Neutral if no indicators available
                
        except Exception as e:
            logger.error(f"Error calculating technical score: {e}")
            return 0.5
    
    def analyze(self, df: pd.DataFrame) -> Dict:
        """
        Perform complete technical analysis on price data
        
        Args:
            df: DataFrame with OHLCV data
            Must have columns: open, high, low, close, volume
            
        Returns:
            Dict with all technical indicators and composite score
        """
        try:
            # Calculate indicators
            ema20 = self.calculate_ema(df, period=20)
            ema50 = self.calculate_ema(df, period=50)
            rsi = self.calculate_rsi(df, period=14)
            macd_data = self.calculate_macd(df)
            
            # Get latest values
            latest_idx = len(df) - 1
            ema20_val = ema20.iloc[latest_idx] if len(ema20) > latest_idx else None
            ema50_val = ema50.iloc[latest_idx] if len(ema50) > latest_idx else None
            rsi_val = rsi.iloc[latest_idx] if len(rsi) > latest_idx else None
            macd_val = macd_data['macd'].iloc[latest_idx] if len(macd_data['macd']) > latest_idx else None
            
            # Calculate technical score
            technical_score = self.calculate_technical_score(
                ema20_val if not pd.isna(ema20_val) else None,
                ema50_val if not pd.isna(ema50_val) else None,
                rsi_val if not pd.isna(rsi_val) else None,
                macd_val if not pd.isna(macd_val) else None
            )
            
            return {
                "ema20": float(ema20_val) if not pd.isna(ema20_val) and ema20_val is not None else None,
                "ema50": float(ema50_val) if not pd.isna(ema50_val) and ema50_val is not None else None,
                "rsi": float(rsi_val) if not pd.isna(rsi_val) and rsi_val is not None else None,
                "macd": float(macd_val) if not pd.isna(macd_val) and macd_val is not None else None,
                "technical_score": technical_score
            }
            
        except Exception as e:
            logger.error(f"Error in technical analysis: {e}")
            return {
                "ema20": None,
                "ema50": None,
                "rsi": None,
                "macd": None,
                "technical_score": 0.5
            }


# Global instance
_indicators: Optional[TechnicalIndicators] = None

def get_indicators() -> TechnicalIndicators:
    """Get or create the global technical indicators instance"""
    global _indicators
    if _indicators is None:
        _indicators = TechnicalIndicators()
    return _indicators


# Example usage
if __name__ == "__main__":
    # Create sample data
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    prices = 100 + np.cumsum(np.random.randn(100).cumsum())
    
    sample_df = pd.DataFrame({
        'date': dates,
        'open': prices + np.random.randn(100) * 2,
        'high': prices + np.abs(np.random.randn(100) * 3),
        'low': prices - np.abs(np.random.randn(100) * 3),
        'close': prices + np.random.randn(100) * 1,
        'volume': np.random.randint(1000000, 10000000, 100)
    })
    
    # Calculate indicators
    indicators = get_indicators()
    results = indicators.analyze(sample_df)
    
    print("\n" + "="*70)
    print("Technical Indicators Test Results")
    print("="*70)
    print(f"EMA 20: {results['ema20']:.2f}")
    print(f"EMA 50: {results['ema50']:.2f}")
    print(f"RSI: {results['rsi']:.2f}")
    print(f"MACD: {results['macd']:.4f}")
    print(f"Technical Score: {results['technical_score']:.4f}")

