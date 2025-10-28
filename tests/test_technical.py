"""
Test suite for technical indicators module
"""

import pytest
import pandas as pd
import numpy as np
from ml_service.indicators import TechnicalIndicators


class TestTechnicalIndicators:
    """Test cases for technical indicators"""
    
    @pytest.fixture
    def indicators(self):
        """Create indicators instance for testing"""
        return TechnicalIndicators()
    
    @pytest.fixture
    def sample_data(self):
        """Create sample market data"""
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100).cumsum())
        
        return pd.DataFrame({
            'date': dates,
            'open': prices + np.random.randn(100) * 2,
            'high': prices + np.abs(np.random.randn(100) * 3),
            'low': prices - np.abs(np.random.randn(100) * 3),
            'close': prices + np.random.randn(100) * 1,
            'volume': np.random.randint(1000000, 10000000, 100)
        })
    
    def test_calculate_ema(self, indicators, sample_data):
        """Test EMA calculation"""
        ema = indicators.calculate_ema(sample_data, period=20)
        
        assert ema is not None
        assert len(ema) > 0
    
    def test_calculate_rsi(self, indicators, sample_data):
        """Test RSI calculation"""
        rsi = indicators.calculate_rsi(sample_data, period=14)
        
        assert rsi is not None
        assert len(rsi) > 0
        # RSI should be between 0 and 100
        assert all(0 <= val <= 100 for val in rsi if not pd.isna(val))
    
    def test_calculate_macd(self, indicators, sample_data):
        """Test MACD calculation"""
        macd_data = indicators.calculate_macd(sample_data)
        
        assert macd_data is not None
        assert "macd" in macd_data
        assert "signal" in macd_data
        assert "histogram" in macd_data
    
    def test_calculate_technical_score(self, indicators):
        """Test technical score calculation"""
        score = indicators.calculate_technical_score(
            ema20=105.0,
            ema50=100.0,
            rsi=65.0,
            macd=2.5
        )
        
        assert 0 <= score <= 1
        # With these values, should be bullish
        assert score > 0.5
    
    def test_calculate_technical_score_bearish(self, indicators):
        """Test technical score for bearish scenario"""
        score = indicators.calculate_technical_score(
            ema20=95.0,
            ema50=100.0,
            rsi=35.0,
            macd=-2.5
        )
        
        assert 0 <= score <= 1
        # Should be bearish
        assert score < 0.5
    
    def test_analyze(self, indicators, sample_data):
        """Test complete technical analysis"""
        result = indicators.analyze(sample_data)
        
        assert result is not None
        assert "ema20" in result
        assert "ema50" in result
        assert "rsi" in result
        assert "macd" in result
        assert "technical_score" in result
        assert 0 <= result["technical_score"] <= 1
    
    def test_technical_score_with_none_values(self, indicators):
        """Test handling of None values"""
        score = indicators.calculate_technical_score(
            ema20=None,
            ema50=None,
            rsi=None,
            macd=None
        )
        
        assert score == 0.5  # Should default to neutral


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

