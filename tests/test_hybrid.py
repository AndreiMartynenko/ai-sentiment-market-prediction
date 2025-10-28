"""
Test suite for hybrid decision engine
"""

import pytest
from ml_service.hybrid_engine import HybridEngine, Signal


class TestHybridEngine:
    """Test cases for hybrid decision engine"""
    
    @pytest.fixture
    def engine(self):
        """Create hybrid engine instance for testing"""
        return HybridEngine(sentiment_weight=0.4, technical_weight=0.6)
    
    def test_generate_buy_signal(self, engine):
        """Test generation of BUY signal"""
        result = engine.generate_signal(
            sentiment_score=0.85,
            technical_score=0.80
        )
        
        assert result is not None
        assert result["signal"] == "BUY"
        assert result["hybrid_score"] > 0.65
        assert "confidence" in result
        assert "reason" in result
    
    def test_generate_sell_signal(self, engine):
        """Test generation of SELL signal"""
        result = engine.generate_signal(
            sentiment_score=0.20,
            technical_score=0.15
        )
        
        assert result is not None
        assert result["signal"] == "SELL"
        assert result["hybrid_score"] < 0.35
        assert "confidence" in result
    
    def test_generate_hold_signal(self, engine):
        """Test generation of HOLD signal"""
        result = engine.generate_signal(
            sentiment_score=0.50,
            technical_score=0.52
        )
        
        assert result is not None
        assert result["signal"] == "HOLD"
        assert 0.35 < result["hybrid_score"] < 0.65
    
    def test_weight_adjustment(self, engine):
        """Test dynamic weight adjustment"""
        initial_weights = (engine.sentiment_weight, engine.technical_weight)
        
        engine.adjust_weights(0.6, 0.4)
        
        assert engine.sentiment_weight == 0.6
        assert engine.technical_weight == 0.4
        # Verify weights are normalized
        assert abs(engine.sentiment_weight + engine.technical_weight - 1.0) < 0.01
    
    def test_confidence_adjustment(self, engine):
        """Test signal generation with confidence adjustment"""
        result = engine.generate_signal(
            sentiment_score=0.90,
            technical_score=0.85,
            sentiment_confidence=0.5,  # Lower confidence
            technical_confidence=1.0   # Higher confidence
        )
        
        assert result is not None
        # Technical should have more weight due to higher confidence
        assert "confidence" in result["weight_used"]
    
    def test_extreme_sentiment_positive(self, engine):
        """Test with extremely positive sentiment"""
        result = engine.generate_signal(
            sentiment_score=0.95,
            technical_score=0.40
        )
        
        assert result is not None
        # Strong sentiment should push towards BUY
        assert result["signal"] in ["BUY", "HOLD"]
    
    def test_extreme_sentiment_negative(self, engine):
        """Test with extremely negative sentiment"""
        result = engine.generate_signal(
            sentiment_score=0.05,
            technical_score=0.60
        )
        
        assert result is not None
        # Very negative sentiment should push towards SELL
        assert result["signal"] in ["SELL", "HOLD"]
    
    def test_generate_reason(self, engine):
        """Test reason generation"""
        result = engine.generate_signal(
            sentiment_score=0.75,
            technical_score=0.70
        )
        
        assert "reason" in result
        assert result["reason"] is not None
        assert len(result["reason"]) > 0
        assert "bullish" in result["reason"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

